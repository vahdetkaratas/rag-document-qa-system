"""
Embedding with sentence-transformers (default: all-MiniLM-L6-v2), normalize_embeddings=True.

**EMBEDDING_MODEL** (env): passed to ``SentenceTransformer(...)`` after resolution:

- **Hugging Face id** (default ``sentence-transformers/all-MiniLM-L6-v2``): downloads on first
  load into the HF cache if not already cached — requires outbound access to huggingface.co.
- **Local directory**: absolute path, or path relative to **project root** (``RAG_PROJECT_ROOT`` /
  repo root) if that directory exists. Relative paths are **not** resolved from process **cwd**.

Use a local path in Docker when the runtime network cannot reach Hugging Face (bake model at
image build, or mount a volume with ``huggingface-cli download`` / ``snapshot_download`` output
laid out as a sentence-transformers model folder).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import numpy as np

from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
NORMALIZE = True

_model = None


def _raw_embedding_model_spec() -> str:
    return (os.getenv("EMBEDDING_MODEL") or "").strip() or DEFAULT_EMBEDDING_MODEL_ID


def resolve_embedding_model(spec: str | None = None) -> str:
    """
    Return the string passed to ``SentenceTransformer``: a local directory path, or a Hub model id.

    Resolution order:
    1. If *spec* (or env) points to an **existing absolute** directory → use it (resolved).
    2. Else **PROJECT_ROOT / spec** if that directory exists (resolved).
    3. Else treat the string as a **Hugging Face model id** (no cwd-based path lookup).
    """
    raw = (spec if spec is not None else _raw_embedding_model_spec()).strip()
    if not raw:
        raw = DEFAULT_EMBEDDING_MODEL_ID

    abs_path = Path(raw)
    if abs_path.is_absolute():
        if abs_path.is_dir():
            return str(abs_path.resolve())
        logger.warning("EMBEDDING_MODEL is absolute but not a directory: %s — trying as Hub id", raw)

    under_root = (PROJECT_ROOT / raw).resolve()
    if under_root.is_dir():
        return str(under_root)

    return raw


def load_embedding_model():
    """Load sentence-transformers model (lazy singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        resolved = resolve_embedding_model()
        logger.info("Loading SentenceTransformer from: %s", resolved)
        _model = SentenceTransformer(resolved)
    return _model


def embed_texts(texts: list[str], model=None) -> np.ndarray:
    """
    Embed list of texts. Returns (n, dim) float32 array, L2-normalized if NORMALIZE.
    """
    if model is None:
        model = load_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=NORMALIZE)
    return embeddings.astype(np.float32)
