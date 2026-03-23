"""Optional RAG_API_KEY header validation."""
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app_with_rag_key(monkeypatch):
    monkeypatch.setenv("RAG_API_KEY", "secret-demo-key")
    monkeypatch.setenv("API_RATE_LIMIT", "off")
    import src.api.app as app_mod

    importlib.reload(app_mod)
    yield app_mod.app
    monkeypatch.delenv("RAG_API_KEY", raising=False)
    monkeypatch.delenv("API_RATE_LIMIT", raising=False)
    importlib.reload(app_mod)


def test_ask_without_key_401(app_with_rag_key):
    with TestClient(app_with_rag_key) as client:
        r = client.post("/ask", json={"question": "hello?"})
    assert r.status_code == 401


def test_ask_with_x_rag_api_key(app_with_rag_key):
    with TestClient(app_with_rag_key) as client:
        r = client.post(
            "/ask",
            json={"question": "hello?"},
            headers={"X-RAG-API-Key": "secret-demo-key"},
        )
    assert r.status_code in (200, 503)


def test_ask_with_bearer_token(app_with_rag_key):
    with TestClient(app_with_rag_key) as client:
        r = client.post(
            "/ask",
            json={"question": "hello?"},
            headers={"Authorization": "Bearer secret-demo-key"},
        )
    assert r.status_code in (200, 503)
