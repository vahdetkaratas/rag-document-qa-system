"""
Embedding with sentence-transformers/all-MiniLM-L6-v2, normalize_embeddings=True. RAG_SYSTEM_DESIGN §4, IMPLEMENTATION_REFERENCE §4.
"""
import numpy as np

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
NORMALIZE = True

_model = None


def load_embedding_model():
    """Load sentence-transformers model (lazy)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str], model=None) -> np.ndarray:
    """
    Embed list of texts. Returns (n, dim) float32 array, L2-normalized if NORMALIZE.
    """
    if model is None:
        model = load_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=NORMALIZE)
    return embeddings.astype(np.float32)
