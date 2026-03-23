"""
FAISS IndexFlatIP (inner product; use with normalized embeddings for cosine-like search). IMPLEMENTATION_REFERENCE §5.
"""
from pathlib import Path

import numpy as np

# Default paths
from src.config import EMBEDDINGS_PATH, FAISS_INDEX_PATH, METADATA_PATH


def save_faiss_index(embeddings: np.ndarray, index_path: str | Path | None = None) -> Path:
    """Build FAISS IndexFlatIP from embeddings (float32) and save. Returns path."""
    import faiss

    index_path = Path(index_path or FAISS_INDEX_PATH)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    faiss.write_index(index, str(index_path))
    return index_path


def load_faiss_index(index_path: str | Path | None = None):
    """Load FAISS index from path. Returns faiss.Index."""
    import faiss

    index_path = Path(index_path or FAISS_INDEX_PATH)
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found: {index_path}. Run indexing pipeline first.")
    return faiss.read_index(str(index_path))
