import sqlite3


def criar_confirmacao(conn: sqlite3.Connection, id_agendamento: int,
                      data_hora_prevista: str | None,
                      data_hora_confirmacao: str | None,
                      status: str) -> dict:
    cursor = conn.execute(
        """INSERT INTO confirmacoes
           (id_agendamento, data_hora_prevista, data_hora_confirmacao, status)
           VALUES (?, ?, ?, ?)""",
        (id_agendamento, data_hora_prevista, data_hora_confirmacao, status),
    )
    conn.commit()
    return buscar_confirmacao_por_id(conn, cursor.lastrowid)


def listar_confirmacoes(conn: sqlite3.Connection, id_usuario: int | None = None) -> list[dict]:
    if id_usuario is not None:
        rows = conn.execute(
            """SELECT c.* FROM confirmacoes c
               JOIN agendamentos a ON c.id_agendamento = a.id
               JOIN medicamentos m ON a.id_medicamento = m.id
               WHERE m.id_usuario = ?""",
            (id_usuario,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM confirmacoes").fetchall()
    return [dict(row) for row in rows]


def buscar_confirmacao_por_id(conn: sqlite3.Connection, confirmacao_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM confirmacoes WHERE id = ?", (confirmacao_id,)
    ).fetchone()
    return dict(row) if row else None


def atualizar_confirmacao(conn: sqlite3.Connection, confirmacao_id: int,
                          status: str,
                          data_hora_confirmacao: str) -> dict | None:
    conn.execute(
        """UPDATE confirmacoes
           SET status = ?, data_hora_confirmacao = ?
           WHERE id = ?""",
        (status, data_hora_confirmacao, confirmacao_id),
    )
    conn.commit()
    return buscar_confirmacao_por_id(conn, confirmacao_id)


def pertence_ao_usuario(conn: sqlite3.Connection, confirmacao_id: int, id_usuario: int) -> bool:
    row = conn.execute(
        """SELECT c.id FROM confirmacoes c
           JOIN agendamentos a ON c.id_agendamento = a.id
           JOIN medicamentos m ON a.id_medicamento = m.id
           WHERE c.id = ? AND m.id_usuario = ?""",
        (confirmacao_id, id_usuario),
    ).fetchone()
    return row is not None
