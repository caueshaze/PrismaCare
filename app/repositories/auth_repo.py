import sqlite3
from datetime import datetime, timezone


def criar_refresh_token(
    conn: sqlite3.Connection,
    user_id: int,
    session_id: str,
    token_hash: str,
    expires_at: str,
    ip: str | None,
    user_agent: str | None,
) -> None:
    conn.execute(
        """INSERT INTO refresh_tokens
           (user_id, session_id, token_hash, expires_at, revoked, created_at, ip, user_agent)
           VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
        (user_id, session_id, token_hash, expires_at, _now_iso(), ip, user_agent),
    )
    conn.commit()


def buscar_refresh_token_ativo(
    conn: sqlite3.Connection,
    token_hash: str,
) -> dict | None:
    row = conn.execute(
        """SELECT * FROM refresh_tokens
           WHERE token_hash = ? AND revoked = 0 AND expires_at > ?""",
        (token_hash, _now_iso()),
    ).fetchone()
    return dict(row) if row else None


def revogar_refresh_token(conn: sqlite3.Connection, token_hash: str) -> None:
    conn.execute(
        "UPDATE refresh_tokens SET revoked = 1, revoked_at = ? WHERE token_hash = ?",
        (_now_iso(), token_hash),
    )
    conn.commit()


def revogar_sessao(conn: sqlite3.Connection, session_id: str, user_id: int) -> int:
    cursor = conn.execute(
        """UPDATE refresh_tokens
           SET revoked = 1, revoked_at = ?
           WHERE session_id = ? AND user_id = ? AND revoked = 0""",
        (_now_iso(), session_id, user_id),
    )
    conn.commit()
    return cursor.rowcount


def revogar_todas_sessoes(conn: sqlite3.Connection, user_id: int) -> int:
    cursor = conn.execute(
        """UPDATE refresh_tokens
           SET revoked = 1, revoked_at = ?
           WHERE user_id = ? AND revoked = 0""",
        (_now_iso(), user_id),
    )
    conn.commit()
    return cursor.rowcount


def registrar_evento_auth(
    conn: sqlite3.Connection,
    event: str,
    success: bool,
    user_id: int | None,
    email: str | None,
    ip: str | None,
    user_agent: str | None,
    reason: str | None = None,
) -> None:
    conn.execute(
        """INSERT INTO auth_events
           (event, success, user_id, email, ip, user_agent, reason, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (event, int(success), user_id, email, ip, user_agent, reason, _now_iso()),
    )
    conn.commit()


def buscar_login_attempt(conn: sqlite3.Connection, email: str, ip: str | None) -> dict | None:
    row = conn.execute(
        "SELECT * FROM login_attempts WHERE email = ? AND ip = ?",
        (email, ip or ""),
    ).fetchone()
    return dict(row) if row else None


def registrar_falha_login(
    conn: sqlite3.Connection,
    email: str,
    ip: str | None,
    threshold: int,
    base_lockout_minutes: int,
    max_lockout_minutes: int,
) -> dict:
    current = buscar_login_attempt(conn, email, ip)
    now = _now_iso()

    if not current:
        conn.execute(
            """INSERT INTO login_attempts (email, ip, failed_count, last_failed_at, locked_until)
               VALUES (?, ?, 1, ?, NULL)""",
            (email, ip or "", now),
        )
        conn.commit()
        return {"failed_count": 1, "locked_until": None}

    failed_count = int(current["failed_count"]) + 1
    locked_until = current["locked_until"]

    if failed_count >= threshold:
        steps = failed_count - threshold + 1
        lock_minutes = min(base_lockout_minutes * steps, max_lockout_minutes)
        lock_until_dt = datetime.now(timezone.utc).timestamp() + (lock_minutes * 60)
        locked_until = datetime.fromtimestamp(lock_until_dt, timezone.utc).isoformat()

    conn.execute(
        """UPDATE login_attempts
           SET failed_count = ?, last_failed_at = ?, locked_until = ?
           WHERE email = ? AND ip = ?""",
        (failed_count, now, locked_until, email, ip or ""),
    )
    conn.commit()
    return {"failed_count": failed_count, "locked_until": locked_until}


def resetar_falhas_login(conn: sqlite3.Connection, email: str, ip: str | None) -> None:
    conn.execute(
        "DELETE FROM login_attempts WHERE email = ? AND ip = ?",
        (email, ip or ""),
    )
    conn.commit()


def login_bloqueado(conn: sqlite3.Connection, email: str, ip: str | None) -> tuple[bool, str | None]:
    current = buscar_login_attempt(conn, email, ip)
    if not current or not current.get("locked_until"):
        return False, None

    locked_until = current["locked_until"]
    if locked_until > _now_iso():
        return True, locked_until

    # lock expirou
    conn.execute(
        "UPDATE login_attempts SET locked_until = NULL WHERE email = ? AND ip = ?",
        (email, ip or ""),
    )
    conn.commit()
    return False, None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
