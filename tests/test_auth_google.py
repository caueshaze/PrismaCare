from app.database import get_connection
from tests.conftest import USUARIO_A


def _google_payload(**overrides):
    payload = {
        "sub": "google-sub-123",
        "email": "google.user@example.com",
        "email_verified": True,
        "name": "Google User",
        "picture": "https://example.com/avatar.png",
        "aud": "test-google-web-client-id.apps.googleusercontent.com",
    }
    payload.update(overrides)
    return payload


def _google_login(client, monkeypatch, payload=None, side_effect=None):
    from app.routes import auth_route

    def fake_verify(*args, **kwargs):
        if side_effect is not None:
            raise side_effect
        return payload or _google_payload()

    monkeypatch.setattr(auth_route.google_id_token, "verify_oauth2_token", fake_verify)
    return client.post("/api/auth/google", json={"id_token": "fake-google-token"})


def test_google_login_cria_usuario_novo(client, monkeypatch):
    r = _google_login(client, monkeypatch)
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == "google.user@example.com"

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT email, nome, telefone, auth_provider, google_sub, avatar_url, timezone_confirmed FROM users WHERE email = ?",
            ("google.user@example.com",),
        ).fetchone()
        assert row is not None
        assert row["nome"] == "Google User"
        assert row["telefone"] is None
        assert row["auth_provider"] == "google"
        assert row["google_sub"] == "google-sub-123"
        assert row["avatar_url"] == "https://example.com/avatar.png"
        assert row["timezone_confirmed"] == 0
    finally:
        conn.close()


def test_google_login_reutiliza_usuario_por_google_sub(client, monkeypatch):
    first = _google_login(client, monkeypatch, payload=_google_payload(name="Primeiro Nome"))
    assert first.status_code == 200
    first_user_id = first.json()["user"]["id"]

    second = _google_login(
        client,
        monkeypatch,
        payload=_google_payload(name="Nome Atualizado", email="outro@example.com"),
    )
    assert second.status_code == 200
    assert second.json()["user"]["id"] == first_user_id

    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) AS total FROM users WHERE google_sub = ?", ("google-sub-123",)).fetchone()
        assert count["total"] == 1
    finally:
        conn.close()


def test_google_login_vincula_conta_local_existente_mesmo_email(client, monkeypatch):
    r = client.post("/api/users", json=USUARIO_A)
    assert r.status_code == 201
    local_user_id = r.json()["id"]

    google = _google_login(
        client,
        monkeypatch,
        payload=_google_payload(email=USUARIO_A["email"], sub="google-sub-local-link"),
    )
    assert google.status_code == 200
    assert google.json()["user"]["id"] == local_user_id

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT auth_provider, google_sub FROM users WHERE id = ?",
            (local_user_id,),
        ).fetchone()
        assert row["auth_provider"] == "local"
        assert row["google_sub"] == "google-sub-local-link"
    finally:
        conn.close()


def test_google_login_rejeita_token_invalido(client, monkeypatch):
    r = _google_login(client, monkeypatch, side_effect=ValueError("invalid"))
    assert r.status_code == 401
    assert r.json()["detail"] == "Token Google inválido"


def test_google_login_rejeita_audience_invalido(client, monkeypatch):
    r = _google_login(client, monkeypatch, payload=_google_payload(aud="wrong-audience"))
    assert r.status_code == 401
    assert r.json()["detail"] == "Token Google inválido"


def test_google_login_rejeita_email_nao_verificado(client, monkeypatch):
    r = _google_login(client, monkeypatch, payload=_google_payload(email_verified=False))
    assert r.status_code == 401
    assert r.json()["detail"] == "Conta Google precisa ter e-mail verificado"
