from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import deps
from app.main import app


class DummyDB:
    def close(self):
        return None


def test_login_success(monkeypatch):
    client = TestClient(app)

    def fake_db():
        yield DummyDB()

    app.dependency_overrides[deps.get_db] = fake_db

    fake_user = SimpleNamespace(
        user_id=1,
        full_name="Planner User",
        email="planner@logitracks.local",
        role="planner",
        is_active=True,
        created_at="2026-04-10T00:00:00Z",
    )

    monkeypatch.setattr("app.api.routers.auth.authenticate_user", lambda db, email, password: fake_user)

    response = client.post("/api/auth/login", json={"email": "planner@logitracks.local", "password": "planner123"})
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "planner"
    assert body["access_token"]
    app.dependency_overrides = {}


def test_admin_only_master_mutation_blocked_for_analyst():
    client = TestClient(app)
    app.dependency_overrides[deps.get_current_user] = lambda: SimpleNamespace(role="analyst", email="analyst@x", is_active=True)

    response = client.post("/api/master/products", json={"sku_code": "X-1"})
    assert response.status_code == 403
    app.dependency_overrides = {}
