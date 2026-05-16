import sqlite3


def test_init_db_saneia_confirmacoes_duplicadas_antes_do_indice_unico(tmp_path, monkeypatch):
    db_path = str(tmp_path / "confirmacoes-duplicadas.db")
    monkeypatch.setattr("app.database.DATABASE_PATH", db_path)

    from app.database import get_connection, init_db

    init_db()

    conn = get_connection()
    try:
        conn.execute("DROP INDEX idx_confirmacoes_agendamento_horario")

        conn.execute(
            """
            INSERT INTO users (nome, telefone, email, senha)
            VALUES (?, ?, ?, ?)
            """,
            ("Ana", "11999990000", "ana@example.com", "senha123"),
        )
        conn.execute(
            """
            INSERT INTO medicamentos (id_usuario, nome, dosagem, observacao)
            VALUES (?, ?, ?, ?)
            """,
            (1, "Losartana", "50mg", ""),
        )
        conn.execute(
            """
            INSERT INTO contatos (id_usuario, nome, telefone, parentesco)
            VALUES (?, ?, ?, ?)
            """,
            (1, "Cuidador", "11988887777", "Filho"),
        )
        conn.execute(
            """
            INSERT INTO agendamentos (id_medicamento, horario, frequencia, data_inicio)
            VALUES (?, ?, ?, ?)
            """,
            (1, "08:00", "diario", "2026-05-16"),
        )

        conn.execute(
            """
            INSERT INTO confirmacoes (id_agendamento, data_hora_prevista, status)
            VALUES (?, ?, ?)
            """,
            (1, "2026-05-16 08:00:00", "PENDENTE"),
        )
        conn.execute(
            """
            INSERT INTO confirmacoes (
                id_agendamento,
                data_hora_prevista,
                data_hora_confirmacao,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (1, "2026-05-16 08:00:00", "2026-05-16 08:05:00", "CONFIRMADO"),
        )
        conn.execute(
            """
            INSERT INTO notificacoes (
                id_contato,
                id_confirmacao,
                data_hora_envio,
                tipo_mensagem,
                status_envio
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, 1, "2026-05-16 08:40:00", "WHATSAPP_SIMULADO", "ENVIADO"),
        )
        conn.execute(
            """
            INSERT INTO notificacoes (
                id_contato,
                id_confirmacao,
                data_hora_envio,
                tipo_mensagem,
                status_envio
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, 2, "2026-05-16 08:41:00", "WHATSAPP_SIMULADO", "FALHA"),
        )
        conn.commit()
    finally:
        conn.close()

    init_db()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        confirmacoes = conn.execute(
            """
            SELECT id, status, data_hora_confirmacao
            FROM confirmacoes
            WHERE id_agendamento = ? AND data_hora_prevista = ?
            """,
            (1, "2026-05-16 08:00:00"),
        ).fetchall()
        assert len(confirmacoes) == 1
        assert confirmacoes[0]["status"] == "CONFIRMADO"
        assert confirmacoes[0]["data_hora_confirmacao"] == "2026-05-16 08:05:00"

        notificacoes = conn.execute(
            """
            SELECT id_confirmacao, id_contato, status_envio
            FROM notificacoes
            ORDER BY status_envio
            """
        ).fetchall()
        assert len(notificacoes) == 1
        assert notificacoes[0]["id_confirmacao"] == confirmacoes[0]["id"]

        indices = conn.execute(
            """
            SELECT name, sql
            FROM sqlite_master
            WHERE type = 'index' AND name = 'idx_confirmacoes_agendamento_horario'
            """
        ).fetchall()
        assert len(indices) == 1
        assert "UNIQUE INDEX" in indices[0]["sql"].upper()
    finally:
        conn.close()
