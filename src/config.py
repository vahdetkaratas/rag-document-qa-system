"""
Project root: one level above src/, or RAG_PROJECT_ROOT env if set (Docker/VPS).
"""
import os
from pathlib import Path

_env_root = (os.getenv("RAG_PROJECT_ROOT") or "").strip()
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DOCS_DIR = PROJECT_ROOT / "data" / "raw_docs"
EXTRACTION_OUTPUT = PROJECT_ROOT / "artifacts" / "extraction" / "extracted_documents.csv"
CHUNK_OUTPUT = PROJECT_ROOT / "artifacts" / "chunks" / "chunked_documents.csv"
EMBEDDINGS_PATH = PROJECT_ROOT / "artifacts" / "embeddings" / "chunk_embeddings.npy"
METADATA_PATH = PROJECT_ROOT / "artifacts" / "embeddings" / "chunk_metadata.csv"
FAISS_INDEX_PATH = PROJECT_ROOT / "artifacts" / "faiss_index" / "index.faiss"
# Written next to the FAISS file at index build; validated at API startup when the index exists.
EMBEDDING_MANIFEST_PATH = FAISS_INDEX_PATH.parent / "embedding_manifest.json"
EVAL_QUESTIONS_PATH = PROJECT_ROOT / "data" / "eval" / "eval_questions.csv"
EVAL_RESULTS_DIR = PROJECT_ROOT / "artifacts" / "eval_results"
