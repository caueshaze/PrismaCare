import sqlite3


def _gerar_confirmacoes_do_dia(conn: sqlite3.Connection, id_usuario: int) -> None:
    """Cria confirmações PENDENTE para agendamentos ativos de hoje que ainda não as têm."""
    conn.execute(
        """
        INSERT INTO confirmacoes (id_agendamento, data_hora_prevista, status)
        SELECT
            a.id,
            date('now') || ' ' || a.horario || ':00',
            'PENDENTE'
        FROM agendamentos a
        JOIN medicamentos m ON a.id_medicamento = m.id
        WHERE m.id_usuario = ?
          AND a.ativo = 1
          AND date('now') >= date(a.data_inicio)
          AND (a.data_fim IS NULL OR date('now') <= date(a.data_fim))
          AND NOT EXISTS (
              SELECT 1 FROM confirmacoes c2
              WHERE c2.id_agendamento = a.id
                AND date(c2.data_hora_prevista) = date('now')
          )
        """,
        (id_usuario,),
    )
    conn.commit()


def listar_doses_hoje(conn: sqlite3.Connection, id_usuario: int) -> list[dict]:
    _gerar_confirmacoes_do_dia(conn, id_usuario)
    rows = conn.execute(
        """
        SELECT
            c.id                        AS confirmacao_id,
            c.data_hora_prevista        AS horario_previsto,
            c.data_hora_confirmacao     AS horario_confirmacao,
            c.status                    AS status,
            m.nome                      AS med_nome,
            m.dosagem                   AS med_dosagem,
            m.observacao                AS med_observacao
        FROM confirmacoes c
        JOIN agendamentos a  ON c.id_agendamento = a.id
        JOIN medicamentos m  ON a.id_medicamento = m.id
        WHERE m.id_usuario = ?
          AND date(c.data_hora_prevista) = date('now')
        ORDER BY c.data_hora_prevista ASC
        """,
        (id_usuario,),
    ).fetchall()

    resultado = []
    for row in rows:
        r = dict(row)
        resultado.append({
            "confirmacao_id":      r["confirmacao_id"],
            "horario_previsto":    r["horario_previsto"],
            "horario_confirmacao": r["horario_confirmacao"],
            "status":              r["status"],
            "medicamento": {
                "nome":       r["med_nome"],
                "dosagem":    r["med_dosagem"],
                "observacao": r["med_observacao"],
            },
        })
    return resultado