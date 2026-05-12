import sqlite3


def criar_medicamento(conn: sqlite3.Connection, id_usuario: int, nome: str,
                      dosagem: str, observacao: str | None, ativo: bool) -> dict:
    cursor = conn.execute(
        """INSERT INTO medicamentos (id_usuario, nome, dosagem, observacao, ativo)
           VALUES (?, ?, ?, ?, ?)""",
        (id_usuario, nome, dosagem, observacao, int(ativo)),
    )
    conn.commit()
    return buscar_medicamento_por_id(conn, cursor.lastrowid)


def listar_medicamentos(conn: sqlite3.Connection, id_usuario: int | None = None) -> list[dict]:
    if id_usuario is not None:
        rows = conn.execute(
            "SELECT * FROM medicamentos WHERE id_usuario = ?", (id_usuario,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM medicamentos").fetchall()
    return [_converter(row) for row in rows]


def buscar_medicamento_por_id(conn: sqlite3.Connection, medicamento_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM medicamentos WHERE id = ?", (medicamento_id,)
    ).fetchone()
    return _converter(row) if row else None


def atualizar_medicamento(conn: sqlite3.Connection, medicamento_id: int,
                          nome: str, dosagem: str, observacao: str | None,
                          ativo: bool) -> dict | None:
    conn.execute(
        """UPDATE medicamentos
           SET nome = ?, dosagem = ?, observacao = ?, ativo = ?
           WHERE id = ?""",
        (nome, dosagem, observacao, int(ativo), medicamento_id),
    )
    conn.commit()
    return buscar_medicamento_por_id(conn, medicamento_id)


def deletar_medicamento(conn: sqlite3.Connection, medicamento_id: int) -> bool:
    cursor = conn.execute("DELETE FROM medicamentos WHERE id = ?", (medicamento_id,))
    conn.commit()
    return cursor.rowcount > 0


def _converter(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["ativo"] = bool(d["ativo"])
    return d
