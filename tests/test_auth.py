from tests.conftest import USUARIO_A, registrar_e_logar


def _login(client, dados):
    return client.post(
        "/api/auth/login",
        data={"username": dados["email"], "password": dados["senha"], "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


# ---------- Cadastro ----------

def test_cadastro_retorna_201(client):
    r = client.post("/api/users", json=USUARIO_A)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == USUARIO_A["email"]
    assert "senha" not in body


def test_cadastro_email_duplicado_retorna_400(client):
    client.post("/api/users", json=USUARIO_A)
    r = client.post("/api/users", json=USUARIO_A)
    assert r.status_code == 400


# ---------- Login ----------

def test_login_retorna_access_e_refresh_token(client):
    client.post("/api/users", json=USUARIO_A)
    r = _login(client, USUARIO_A)
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_senha_errada_retorna_401(client):
    client.post("/api/users", json=USUARIO_A)
    errado = {**USUARIO_A, "senha": "errada"}
    r = _login(client, errado)
    assert r.status_code == 401


# ---------- Refresh ----------

def test_refresh_valido_retorna_novos_tokens(client):
    tokens = registrar_e_logar(client, USUARIO_A)
    r = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body


# ---------- Logout ----------

def test_logout_invalida_refresh_token(client):
    tokens = registrar_e_logar(client, USUARIO_A)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    r = client.post("/api/auth/logout", json={"refresh_token": tokens["refresh_token"]}, headers=headers)
    assert r.status_code == 200

    # Após logout, o mesmo refresh_token deve ser rejeitado
    r2 = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r2.status_code == 401


# ---------- Proteção de endpoints ----------

def test_endpoint_sem_token_retorna_401(client):
    r = client.get("/api/users/me")
    assert r.status_code == 401


# ---------- Timezone ----------

def test_usuario_novo_timezone_confirmado_false(client, headers_a):
    r = client.get("/api/users/me", headers=headers_a)
    assert r.status_code == 200
    body = r.json()
    assert "timezone" in body
    assert body["timezone_confirmed"] is False


def test_patch_timezone_valido(client, headers_a):
    r = client.patch(
        "/api/users/me/timezone",
        json={"timezone": "America/Manaus"},
        headers=headers_a,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["timezone"] == "America/Manaus"
    assert body["timezone_confirmed"] is True


def test_patch_timezone_invalido_retorna_422(client, headers_a):
    r = client.patch(
        "/api/users/me/timezone",
        json={"timezone": "banana/timezone"},
        headers=headers_a,
    )
    assert r.status_code == 422


def test_get_me_retorna_timezone_atualizado(client, headers_a):
    client.patch("/api/users/me/timezone", json={"timezone": "America/Manaus"}, headers=headers_a)
    r = client.get("/api/users/me", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["timezone"] == "America/Manaus"
