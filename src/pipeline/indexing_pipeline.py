"""
Indexing: read chunks -> embed -> save embeddings + metadata -> build FAISS index. MILESTONES M3.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.embeddings.embed_chunks import load_embedding_model, embed_texts, resolve_embedding_model
from src.config import CHUNK_OUTPUT
from src.embeddings.embedding_manifest import manifest_path_for_index, write_embedding_manifest
from src.embeddings.vector_store import save_faiss_index, FAISS_INDEX_PATH, EMBEDDINGS_PATH, METADATA_PATH
from src.utils.file_helpers import ensure_dir


def run_indexing_pipeline(
    chunk_path: str | Path | None = None,
    embeddings_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
    index_path: str | Path | None = None,
) -> tuple[Path, Path, Path]:
    """
    Load chunked_documents.csv, embed texts, save .npy + metadata CSV + FAISS index.
    Returns (embeddings_path, metadata_path, index_path).
    """
    chunk_path = Path(chunk_path or CHUNK_OUTPUT)
    embeddings_path = Path(embeddings_path or EMBEDDINGS_PATH)
    metadata_path = Path(metadata_path or METADATA_PATH)
    index_path = Path(index_path or FAISS_INDEX_PATH)

    if not chunk_path.exists():
        raise FileNotFoundError(f"Chunks not found: {chunk_path}. Run run_chunking first.")

    df = pd.read_csv(chunk_path)
    texts = df["text"].fillna("").tolist()
    if not texts:
        raise ValueError("No text in chunks.")

    ensure_dir(embeddings_path.parent)
    ensure_dir(index_path.parent)

    model = load_embedding_model()
    embeddings = embed_texts(texts, model=model)
    np.save(embeddings_path, embeddings)

    # Metadata for retrieval: chunk_id, document_name, page_number, text (and optionally others)
    meta = df[["chunk_id", "document_name", "page_number", "text"]].copy()
    if "chunk_index_within_page" in df.columns:
        meta["chunk_index_within_page"] = df["chunk_index_within_page"]
    if "char_count" in df.columns:
        meta["char_count"] = df["char_count"]
    meta.to_csv(metadata_path, index=False)

    save_faiss_index(embeddings, index_path)
    resolved = resolve_embedding_model()
    dim = int(model.get_sentence_embedding_dimension())
    write_embedding_manifest(manifest_path_for_index(index_path), resolved, dim)
    print(f"Indexing done: {len(embeddings)} chunks, index at {index_path}")
    return embeddings_path, metadata_path, index_path
