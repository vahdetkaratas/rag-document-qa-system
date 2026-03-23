"""
Top-k retrieval from FAISS index. RAG_SYSTEM_DESIGN §4, IMPLEMENTATION_REFERENCE §6.
Returns retrieved chunks with scores (inner product = cosine when normalized).

FAISS index and metadata DataFrame are loaded once per process (preload at FastAPI startup or lazy on first retrieve_top_k).
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.embeddings.embed_chunks import embed_texts
from src.embeddings.vector_store import load_faiss_index

from src.config import FAISS_INDEX_PATH, METADATA_PATH

logger = logging.getLogger(__name__)

_cached_index = None
_cached_meta_df: pd.DataFrame | None = None
_cached_paths: tuple[Path, Path] | None = None


def is_retrieval_loaded() -> bool:
    """True if FAISS index and metadata are cached in memory."""
    return _cached_index is not None and _cached_meta_df is not None


def preload_retrieval(
    index_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
) -> None:
    """
    Load FAISS index and chunk metadata into memory. Idempotent for the same paths.
    Raises FileNotFoundError if files are missing.
    """
    global _cached_index, _cached_meta_df, _cached_paths

    idx_p = Path(index_path or FAISS_INDEX_PATH).resolve()
    meta_p = Path(metadata_path or METADATA_PATH).resolve()

    if _cached_paths == (idx_p, meta_p) and _cached_index is not None and _cached_meta_df is not None:
        return

    if not meta_p.exists():
        logger.error("Chunk metadata file missing: %s", meta_p)
        raise FileNotFoundError(f"Chunk metadata not found: {meta_p}")
    if not idx_p.exists():
        logger.error("FAISS index file missing: %s", idx_p)
        raise FileNotFoundError(f"FAISS index not found: {idx_p}")

    logger.info("Loading FAISS index from %s", idx_p)
    index = load_faiss_index(idx_p)
    logger.info("Loading chunk metadata from %s", meta_p)
    meta_df = pd.read_csv(meta_p)

    _cached_index = index
    _cached_meta_df = meta_df
    _cached_paths = (idx_p, meta_p)
    logger.info(
        "Retrieval assets loaded: index_vectors=%s metadata_rows=%s",
        index.ntotal,
        len(meta_df),
    )


def _ensure_retrieval_loaded(index_path: Path, metadata_path: Path) -> None:
    """Load cache if empty or paths differ from cached."""
    idx_r = index_path.resolve()
    meta_r = metadata_path.resolve()
    if is_retrieval_loaded() and _cached_paths == (idx_r, meta_r):
        return
    preload_retrieval(idx_r, meta_r)


def retrieve_top_k(
    question: str,
    top_k: int = 5,
    index_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
):
    """
    Embed question, search FAISS, return list of dicts with chunk metadata + score.
    Each dict: chunk_id, document_name, page_number, text, score (and optionally chunk_index_within_page, char_count).
    """
    index_path = Path(index_path or FAISS_INDEX_PATH)
    metadata_path = Path(metadata_path or METADATA_PATH)

    _ensure_retrieval_loaded(index_path, metadata_path)

    assert _cached_index is not None and _cached_meta_df is not None

    query_embedding = embed_texts([question])
    scores, indices = _cached_index.search(query_embedding, min(top_k, _cached_index.ntotal))

    meta = _cached_meta_df
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(meta):
            continue
        row = meta.iloc[idx].to_dict()
        row["score"] = float(scores[0][i])
        results.append(row)
    return results
