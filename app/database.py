import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prismacare.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
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
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                data_nascimento TEXT
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
                status TEXT NOT NULL,
                FOREIGN KEY (id_agendamento) REFERENCES agendamentos(id)
            );

            CREATE TABLE IF NOT EXISTS notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_contato INTEGER NOT NULL,
                id_confirmacao INTEGER NOT NULL,
                data_hora_envio TEXT,
                tipo_mensagem TEXT NOT NULL,
                status_envio TEXT NOT NULL,
                FOREIGN KEY (id_contato) REFERENCES contatos(id),
                FOREIGN KEY (id_confirmacao) REFERENCES confirmacoes(id)
            );
        """)
        conn.commit()
    finally:
        conn.close()
