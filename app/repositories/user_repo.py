import sqlite3


def criar_usuario(conn: sqlite3.Connection, nome: str | None, telefone: str | None,
                  email: str, senha: str, data_nascimento: str | None,
                  timezone: str = "America/Sao_Paulo") -> dict:
    cursor = conn.execute(
        """INSERT INTO users (nome, telefone, email, senha, data_nascimento, timezone)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (nome, telefone, email, senha, data_nascimento, timezone),
    )
    conn.commit()
    return buscar_usuario_por_id(conn, cursor.lastrowid)


def atualizar_nome(conn: sqlite3.Connection, user_id: int, nome: str | None) -> dict | None:
    conn.execute(
        "UPDATE users SET nome = ? WHERE id = ?",
        (nome, user_id),
    )
    conn.commit()
    return buscar_usuario_por_id(conn, user_id)


def atualizar_timezone(conn: sqlite3.Connection, user_id: int, timezone: str) -> dict | None:
    conn.execute(
        "UPDATE users SET timezone = ?, timezone_confirmed = 1 WHERE id = ?",
        (timezone, user_id),
    )
    conn.commit()
    return buscar_usuario_por_id(conn, user_id)


def listar_usuarios(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM users").fetchall()
    return [dict(row) for row in rows]


def buscar_usuario_por_id(conn: sqlite3.Connection, user_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def buscar_usuario_por_email(conn: sqlite3.Connection, email: str) -> dict | None:
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def deletar_usuario(conn: sqlite3.Connection, user_id: int) -> bool:
    cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    return cursor.rowcount > 0
