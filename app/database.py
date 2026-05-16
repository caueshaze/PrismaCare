import sqlite3
import os

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "prismacare.db"),
)

# Padrão de datas: o backend usa o timezone IANA de cada usuário para calcular
# datas e horários locais. Timestamps são armazenados como strings no formato
# YYYY-MM-DD HH:MM:SS no horário local do usuário, sem offset.


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                telefone TEXT,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                data_nascimento TEXT,
                timezone TEXT NOT NULL DEFAULT 'America/Sao_Paulo',
                timezone_confirmed INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS medicamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                nome TEXT NOT NULL,
                dosagem TEXT NOT NULL,
                observacao TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_usuario) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                parentesco TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_usuario) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_medicamento INTEGER NOT NULL,
                horario TEXT NOT NULL,
                frequencia TEXT NOT NULL,
                data_inicio TEXT,
                data_fim TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id)
            );

            CREATE TABLE IF NOT EXISTS confirmacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_agendamento INTEGER NOT NULL,
                data_hora_prevista TEXT,
                data_hora_confirmacao TEXT,
                status TEXT NOT NULL CHECK(status IN ('PENDENTE','CONFIRMADO','NAO_CONFIRMADO','CANCELADO')),
                FOREIGN KEY (id_agendamento) REFERENCES agendamentos(id)
            );

            CREATE TABLE IF NOT EXISTS notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_contato INTEGER NOT NULL,
                id_confirmacao INTEGER NOT NULL,
                data_hora_envio TEXT,
                tipo_mensagem TEXT NOT NULL,
                status_envio TEXT NOT NULL CHECK(status_envio IN ('AGUARDANDO','ENVIADO','FALHA')),
                FOREIGN KEY (id_contato) REFERENCES contatos(id),
                FOREIGN KEY (id_confirmacao) REFERENCES confirmacoes(id)
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                revoked_at TEXT,
                ip TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id
            ON refresh_tokens (user_id);

            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_session_id
            ON refresh_tokens (session_id);

            CREATE TABLE IF NOT EXISTS auth_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                success INTEGER NOT NULL,
                user_id INTEGER,
                email TEXT,
                ip TEXT,
                user_agent TEXT,
                reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_auth_events_created_at
            ON auth_events (created_at);

            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                ip TEXT NOT NULL DEFAULT '',
                failed_count INTEGER NOT NULL DEFAULT 0,
                last_failed_at TEXT,
                locked_until TEXT
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_login_attempts_email_ip
            ON login_attempts (email, ip);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_notificacoes_confirmacao_contato
            ON notificacoes (id_confirmacao, id_contato);

            CREATE INDEX IF NOT EXISTS idx_medicamentos_id_usuario
            ON medicamentos (id_usuario);

            CREATE INDEX IF NOT EXISTS idx_confirmacoes_data_hora_prevista
            ON confirmacoes (data_hora_prevista);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_confirmacoes_agendamento_horario
            ON confirmacoes (id_agendamento, data_hora_prevista);
        """)
        conn.commit()

        
        conn.executescript("""
            UPDATE confirmacoes SET status = 'PENDENTE'       WHERE status = 'pendente';
            UPDATE confirmacoes SET status = 'CONFIRMADO'     WHERE status = 'confirmado';
            UPDATE confirmacoes SET status = 'NAO_CONFIRMADO' WHERE status = 'atrasado_notificado';
            UPDATE confirmacoes SET status = 'NAO_CONFIRMADO' WHERE status = 'ATRASADO';
            UPDATE confirmacoes SET status = 'CANCELADO'      WHERE status = 'nao_confirmado';
            UPDATE confirmacoes SET status = 'CANCELADO'      WHERE status = 'cancelado';
            UPDATE notificacoes SET status_envio = 'AGUARDANDO' WHERE status_envio = 'pendente';
            UPDATE notificacoes SET status_envio = 'ENVIADO'    WHERE status_envio = 'enviado';
            UPDATE notificacoes SET status_envio = 'FALHA'      WHERE status_envio = 'falhou';
        """)
        conn.commit()

        for sql in [
            "ALTER TABLE users ADD COLUMN timezone TEXT NOT NULL DEFAULT 'America/Sao_Paulo'",
            "ALTER TABLE users ADD COLUMN timezone_confirmed INTEGER NOT NULL DEFAULT 0",
        ]:
            try:
                conn.execute(sql)
                conn.commit()
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise

        user_columns = conn.execute("PRAGMA table_info(users)").fetchall()
        must_rebuild_users = any(
            column["name"] in {"nome", "telefone"} and column["notnull"] == 1
            for column in user_columns
        )
        if must_rebuild_users:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.executescript("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    telefone TEXT,
                    email TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    data_nascimento TEXT,
                    timezone TEXT NOT NULL DEFAULT 'America/Sao_Paulo',
                    timezone_confirmed INTEGER NOT NULL DEFAULT 0
                );

                INSERT INTO users_new (
                    id, nome, telefone, email, senha, data_nascimento, timezone, timezone_confirmed
                )
                SELECT
                    id,
                    NULLIF(nome, ''),
                    NULLIF(telefone, ''),
                    email,
                    senha,
                    data_nascimento,
                    COALESCE(timezone, 'America/Sao_Paulo'),
                    COALESCE(timezone_confirmed, 0)
                FROM users;

                DROP TABLE users;
                ALTER TABLE users_new RENAME TO users;
            """)
            conn.commit()
            conn.execute("PRAGMA foreign_keys = ON")
    finally:
        conn.close()