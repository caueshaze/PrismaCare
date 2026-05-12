import sqlite3


def criar_agendamento(conn: sqlite3.Connection, id_medicamento: int,
                      horario: str, frequencia: str,
                      data_inicio: str | None, data_fim: str | None,
                      ativo: bool) -> dict:
    cursor = conn.execute(
        """INSERT INTO agendamentos
           (id_medicamento, horario, frequencia, data_inicio, data_fim, ativo)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (id_medicamento, horario, frequencia, data_inicio, data_fim, int(ativo)),
    )
    conn.commit()
    return buscar_agendamento_por_id(conn, cursor.lastrowid)


def listar_agendamentos(conn: sqlite3.Connection, id_usuario: int | None = None) -> list[dict]:
    if id_usuario is not None:
        rows = conn.execute(
            """SELECT a.* FROM agendamentos a
               JOIN medicamentos m ON a.id_medicamento = m.id
               WHERE m.id_usuario = ?""",
            (id_usuario,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM agendamentos").fetchall()
    return [_converter(row) for row in rows]


def buscar_agendamento_por_id(conn: sqlite3.Connection, agendamento_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM agendamentos WHERE id = ?", (agendamento_id,)
    ).fetchone()
    return _converter(row) if row else None


def deletar_agendamento(conn: sqlite3.Connection, agendamento_id: int) -> bool:
    cursor = conn.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
    conn.commit()
    return cursor.rowcount > 0


def pertence_ao_usuario(conn: sqlite3.Connection, agendamento_id: int, id_usuario: int) -> bool:
    row = conn.execute(
        """SELECT a.id FROM agendamentos a
           JOIN medicamentos m ON a.id_medicamento = m.id
           WHERE a.id = ? AND m.id_usuario = ?""",
        (agendamento_id, id_usuario),
    ).fetchone()
    return row is not None


def _converter(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["ativo"] = bool(d["ativo"])
    return d
