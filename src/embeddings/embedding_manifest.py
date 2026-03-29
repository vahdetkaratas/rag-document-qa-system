"""
Minimal embedding contract: manifest written at index build, validated at API startup.
"""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST_FILENAME = "embedding_manifest.json"


def manifest_path_for_index(index_path: str | Path) -> Path:
    return Path(index_path).resolve().parent / MANIFEST_FILENAME


def write_embedding_manifest(
    manifest_path: str | Path,
    resolved_model: str,
    embedding_dim: int,
) -> Path:
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "resolved_embedding_model": resolved_model,
        "embedding_dim": int(embedding_dim),
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def read_embedding_manifest(manifest_path: str | Path) -> dict:
    path = Path(manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"Embedding manifest not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Embedding manifest must be a JSON object: {path}")
    return data


def validate_embedding_contract(
    manifest: dict,
    resolved_model: str,
    embedding_dim: int,
) -> None:
    """
    Compare index-time manifest to the currently resolved model and loaded dimension.
    Raises RuntimeError on mismatch (fail-fast at API startup).
    """
    want_model = manifest.get("resolved_embedding_model")
    want_dim = manifest.get("embedding_dim")
    if want_model is None or want_dim is None:
        raise RuntimeError(
            "Embedding manifest is missing required keys "
            "'resolved_embedding_model' and/or 'embedding_dim'. Re-run indexing."
        )
    if not isinstance(want_dim, int):
        try:
            want_dim = int(want_dim)
        except (TypeError, ValueError) as e:
            raise RuntimeError(
                f"Embedding manifest has invalid embedding_dim: {manifest.get('embedding_dim')!r}"
            ) from e
    if str(want_model) != str(resolved_model):
        raise RuntimeError(
            "Embedding model mismatch: FAISS index was built with "
            f"resolved_embedding_model={want_model!r}, but the API resolves "
            f"EMBEDDING_MODEL to {resolved_model!r}. Use the same model as at index time."
        )
    if int(want_dim) != int(embedding_dim):
        raise RuntimeError(
            f"Embedding dimension mismatch: index manifest has embedding_dim={want_dim}, "
            f"but the loaded model reports dimension {embedding_dim}. Re-build the index "
            "with the configured embedding model."
        )
