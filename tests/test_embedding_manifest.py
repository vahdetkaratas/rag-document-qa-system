"""Embedding manifest write/validate contract (no sentence-transformers load)."""
import pytest

from src.embeddings.embedding_manifest import (
    manifest_path_for_index,
    read_embedding_manifest,
    validate_embedding_contract,
    write_embedding_manifest,
)


def test_manifest_path_for_index(tmp_path):
    idx = tmp_path / "nested" / "index.faiss"
    assert manifest_path_for_index(idx) == tmp_path / "nested" / "embedding_manifest.json"


def test_write_read_roundtrip(tmp_path):
    p = tmp_path / "embedding_manifest.json"
    write_embedding_manifest(p, "/models/minilm", 384)
    m = read_embedding_manifest(p)
    assert m["resolved_embedding_model"] == "/models/minilm"
    assert m["embedding_dim"] == 384


def test_validate_contract_ok():
    validate_embedding_contract(
        {"resolved_embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "embedding_dim": 384},
        "sentence-transformers/all-MiniLM-L6-v2",
        384,
    )


def test_validate_contract_model_mismatch():
    with pytest.raises(RuntimeError, match="Embedding model mismatch"):
        validate_embedding_contract(
            {"resolved_embedding_model": "model-a", "embedding_dim": 384},
            "model-b",
            384,
        )


def test_validate_contract_dim_mismatch():
    with pytest.raises(RuntimeError, match="Embedding dimension mismatch"):
        validate_embedding_contract(
            {"resolved_embedding_model": "x", "embedding_dim": 384},
            "x",
            768,
        )


def test_validate_contract_missing_keys():
    with pytest.raises(RuntimeError, match="missing required keys"):
        validate_embedding_contract({"embedding_dim": 384}, "x", 384)
    with pytest.raises(RuntimeError, match="missing required keys"):
        validate_embedding_contract({"resolved_embedding_model": "x"}, "x", 384)


def test_read_embedding_manifest_missing(tmp_path):
    missing = tmp_path / "nope.json"
    with pytest.raises(FileNotFoundError):
        read_embedding_manifest(missing)


def test_validate_coerces_numeric_dim_string_in_manifest():
    """Manifest may be hand-edited; int-like string still compares to loaded dim."""
    validate_embedding_contract(
        {"resolved_embedding_model": "hub/id", "embedding_dim": "384"},
        "hub/id",
        384,
    )
