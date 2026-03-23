"""
Tests for embeddings and retrieval. MILESTONES M3.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.slow

from src.config import PROJECT_ROOT

from src.embeddings.embed_chunks import embed_texts, load_embedding_model
from src.embeddings.vector_store import save_faiss_index, load_faiss_index

from src.config import CHUNK_OUTPUT as CHUNK_CSV, FAISS_INDEX_PATH as FAISS_INDEX, METADATA_PATH as METADATA_CSV


def test_embed_texts_shape():
    """embed_texts returns (n, dim) float32 array."""
    texts = ["first chunk", "second chunk"]
    emb = embed_texts(texts)
    assert emb.dtype == np.float32
    assert emb.shape[0] == 2
    assert emb.shape[1] > 0


def test_embed_texts_normalized():
    """Embeddings are L2-normalized (norm ~ 1)."""
    emb = embed_texts(["test"])
    n = np.linalg.norm(emb[0])
    assert abs(n - 1.0) < 0.01


def test_save_load_faiss_index():
    """Save and load FAISS index."""
    emb = embed_texts(["a", "b", "c"])
    path = PROJECT_ROOT / "artifacts" / "faiss_index" / "test_index.faiss"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_faiss_index(emb, path)
    index = load_faiss_index(path)
    assert index.ntotal == 3
    path.unlink(missing_ok=True)


def test_retrieve_top_k():
    """retrieve_top_k returns list of dicts with score and metadata."""
    if not FAISS_INDEX.exists() or not METADATA_CSV.exists():
        pytest.skip("Run indexing pipeline first")
    from src.retrieval.retrieve import retrieve_top_k
    results = retrieve_top_k("cancellation policy", top_k=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    if results:
        assert "chunk_id" in results[0] or "document_name" in results[0]
        assert "score" in results[0]
        assert "text" in results[0]
