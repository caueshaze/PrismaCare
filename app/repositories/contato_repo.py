import sqlite3


def criar_contato(conn: sqlite3.Connection, id_usuario: int, nome: str,
                  telefone: str, parentesco: str, ativo: bool) -> dict:
    cursor = conn.execute(
        """INSERT INTO contatos (id_usuario, nome, telefone, parentesco, ativo)
           VALUES (?, ?, ?, ?, ?)""",
        (id_usuario, nome, telefone, parentesco, int(ativo)),
    )
    conn.commit()
    return buscar_contato_por_id(conn, cursor.lastrowid)


def listar_contatos(conn: sqlite3.Connection, id_usuario: int | None = None) -> list[dict]:
    if id_usuario is not None:
        rows = conn.execute(
            "SELECT * FROM contatos WHERE id_usuario = ?", (id_usuario,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM contatos").fetchall()
    return [_converter(row) for row in rows]


def buscar_contato_por_id(conn: sqlite3.Connection, contato_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM contatos WHERE id = ?", (contato_id,)
    ).fetchone()
    return _converter(row) if row else None


def deletar_contato(conn: sqlite3.Connection, contato_id: int) -> bool:
    cursor = conn.execute("DELETE FROM contatos WHERE id = ?", (contato_id,))
    conn.commit()
    return cursor.rowcount > 0


def pertence_ao_usuario(conn: sqlite3.Connection, contato_id: int, id_usuario: int) -> bool:
    row = conn.execute(
        "SELECT id FROM contatos WHERE id = ? AND id_usuario = ?",
        (contato_id, id_usuario),
    ).fetchone()
    return row is not None


def atualizar_contato(conn: sqlite3.Connection, contato_id: int,
                      nome: str | None, telefone: str | None,
                      parentesco: str | None) -> dict | None:
    campos = {"nome": nome, "telefone": telefone, "parentesco": parentesco}
    campos = {k: v for k, v in campos.items() if v is not None}
    set_clause = ", ".join(f"{k} = ?" for k in campos)
    conn.execute(
        f"UPDATE contatos SET {set_clause} WHERE id = ?",
        (*campos.values(), contato_id),
    )
    conn.commit()
    return buscar_contato_por_id(conn, contato_id)


def _converter(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["ativo"] = bool(d["ativo"])
    return d
