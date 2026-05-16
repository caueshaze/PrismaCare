import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_minimal_register_lookup_login_and_profile_update(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "prismacare-test.db"))

    import app.database as database

    importlib.reload(database)

    import app.main as main

    importlib.reload(main)

    with TestClient(main.app) as client:
        email = "caue@example.com"
        password = "segredo123"

        lookup_before = client.post("/api/auth/lookup-email", json={"email": email})
        assert lookup_before.status_code == 200
        assert lookup_before.json() == {"exists": False}

        created = client.post("/api/auth/register", json={"email": email, "password": password})
        assert created.status_code == 201
        created_payload = created.json()
        assert created_payload["email"] == email
        assert created_payload["nome"] is None
        assert created_payload["telefone"] is None
        assert created_payload["timezone_confirmed"] is False

        lookup_after = client.post("/api/auth/lookup-email", json={"email": email})
        assert lookup_after.status_code == 200
        assert lookup_after.json() == {"exists": True}

        login = client.post(
            "/api/auth/login",
            data={"username": email, "password": password, "grant_type": "password"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        me_before = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me_before.status_code == 200
        assert me_before.json()["nome"] is None

        invalid_name = client.patch(
            "/api/users/me",
            json={"name": "C"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invalid_name.status_code == 422

        updated_name = client.patch(
            "/api/users/me",
            json={"name": "Cauê"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert updated_name.status_code == 200
        assert updated_name.json()["nome"] == "Cauê"
