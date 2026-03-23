"""API tests: /health, /ask validation."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Always use current app object (other tests may reload src.api.app)
    import src.api.app as app_mod

    with TestClient(app_mod.app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "ready" in data
    assert isinstance(data["ready"], bool)
    assert "index_file" in data
    assert "metadata_file" in data
    assert "retrieval_loaded" in data


def test_ask_empty_question(client):
    r = client.post("/ask", json={"question": ""})
    # Pydantic validates min_length=1 before the route runs
    assert r.status_code == 422


def test_ask_missing_question(client):
    r = client.post("/ask", json={})
    assert r.status_code == 422
