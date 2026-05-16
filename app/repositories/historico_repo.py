import sqlite3


def listar_historico(
    conn: sqlite3.Connection,
    id_usuario: int,
    data_inicio: str,
    data_fim: str,
) -> list[dict]:
    rows = conn.execute(
        """
        SELECT
            c.id                    AS confirmacao_id,
            a.id                    AS agendamento_id,
            m.id                    AS medicamento_id,
            m.nome                  AS medicamento,
            m.dosagem               AS dosagem,
            c.data_hora_prevista    AS horario_previsto,
            c.data_hora_confirmacao AS horario_confirmacao,
            c.status                AS status
        FROM confirmacoes c
        JOIN agendamentos a ON a.id = c.id_agendamento
        JOIN medicamentos m ON m.id = a.id_medicamento
        WHERE m.id_usuario = ?
          AND date(c.data_hora_prevista) BETWEEN date(?) AND date(?)
        ORDER BY c.data_hora_prevista DESC
        """,
        (id_usuario, data_inicio, data_fim),
    ).fetchall()
    return [dict(row) for row in rows]