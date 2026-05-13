import sqlite3


def criar_notificacao(conn: sqlite3.Connection, id_contato: int,
                      id_confirmacao: int, data_hora_envio: str | None,
                      tipo_mensagem: str, status_envio: str) -> dict:
    cursor = conn.execute(
        """INSERT INTO notificacoes
           (id_contato, id_confirmacao, data_hora_envio, tipo_mensagem, status_envio)
           VALUES (?, ?, ?, ?, ?)""",
        (id_contato, id_confirmacao, data_hora_envio, tipo_mensagem, status_envio),
    )
    conn.commit()
    return buscar_notificacao_por_id(conn, cursor.lastrowid)


def listar_notificacoes(conn: sqlite3.Connection, id_usuario: int | None = None) -> list[dict]:
    if id_usuario is not None:
        rows = conn.execute(
            """SELECT n.* FROM notificacoes n
               JOIN contatos ct ON n.id_contato = ct.id
               WHERE ct.id_usuario = ?""",
            (id_usuario,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM notificacoes").fetchall()
    return [dict(row) for row in rows]


def buscar_notificacao_por_id(conn: sqlite3.Connection, notificacao_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM notificacoes WHERE id = ?", (notificacao_id,)
    ).fetchone()
    return dict(row) if row else None


def notificacao_ja_existe(conn: sqlite3.Connection, id_confirmacao: int, id_contato: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM notificacoes WHERE id_confirmacao = ? AND id_contato = ?",
        (id_confirmacao, id_contato),
    ).fetchone()
    return row is not None


def pertence_ao_usuario(conn: sqlite3.Connection, notificacao_id: int, id_usuario: int) -> bool:
    row = conn.execute(
        """SELECT n.id FROM notificacoes n
           JOIN contatos ct ON n.id_contato = ct.id
           WHERE n.id = ? AND ct.id_usuario = ?""",
        (notificacao_id, id_usuario),
    ).fetchone()
    return row is not None
