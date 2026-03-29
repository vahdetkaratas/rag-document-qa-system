"""Fast tests for EMBEDDING_MODEL path resolution (no Hub download)."""
from pathlib import Path

import pytest

from src.config import PROJECT_ROOT
from src.embeddings.embed_chunks import resolve_embedding_model


def test_resolve_absolute_dir(tmp_path, monkeypatch):
    d = tmp_path / "saved_model"
    d.mkdir()
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    assert resolve_embedding_model(str(d)) == str(d.resolve())


def test_resolve_relative_to_project_root(tmp_path, monkeypatch):
    rel = "models_stub_minilm"
    d = PROJECT_ROOT / rel
    d.mkdir(exist_ok=True)
    try:
        monkeypatch.setenv("EMBEDDING_MODEL", rel)
        assert resolve_embedding_model() == str(d.resolve())
    finally:
        d.rmdir()


def test_resolve_hub_id_when_no_local_dir(monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    assert resolve_embedding_model() == "sentence-transformers/all-MiniLM-L6-v2"


def test_resolve_does_not_use_cwd(tmp_path, monkeypatch):
    """A directory that exists only under cwd is ignored; spec is returned as Hub id."""
    (tmp_path / "models_only_in_cwd").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    assert resolve_embedding_model("models_only_in_cwd") == "models_only_in_cwd"


def test_resolve_relative_missing_under_project_root_is_hub_id(monkeypatch):
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    assert resolve_embedding_model("definitely_not_a_project_subdir_abc123") == (
        "definitely_not_a_project_subdir_abc123"
    )
