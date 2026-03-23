"""
Text extraction from PDF (pymupdf), TXT, MD. RAG_SYSTEM_DESIGN §3.
Output rows: document_name, page_number, text, char_count.
"""
from pathlib import Path

import pandas as pd

from src.ingestion.load_documents import SUPPORTED_EXTENSIONS


def _extract_pdf(path: Path) -> list[dict]:
    """Extract text page by page from PDF. Returns list of dicts with document_name, page_number, text, char_count."""
    import fitz  # pymupdf

    doc = fitz.open(path)
    rows = []
    name = path.name
    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text("text") or ""
        rows.append({
            "document_name": name,
            "page_number": i + 1,
            "text": text.strip(),
            "char_count": len(text),
        })
    doc.close()
    return rows


def _extract_plain_text(path: Path) -> list[dict]:
    """Extract full text from .txt or .md as a single page."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return [{
        "document_name": path.name,
        "page_number": 1,
        "text": text.strip(),
        "char_count": len(text),
    }]


def extract_text_from_file(path: str | Path) -> list[dict]:
    """
    Extract text from a single file. Returns list of dicts: document_name, page_number, text, char_count.
    PDF: one row per page. TXT/MD: one row (page_number=1).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported extension: {path.suffix}. Use {SUPPORTED_EXTENSIONS}")

    if path.suffix.lower() == ".pdf":
        return _extract_pdf(path)
    return _extract_plain_text(path)


def extract_all(raw_docs_dir: str | Path) -> pd.DataFrame:
    """
    Extract text from all supported documents in raw_docs_dir.
    Returns DataFrame with columns: document_name, page_number, text, char_count.
    """
    from src.ingestion.load_documents import list_document_paths

    paths = list_document_paths(raw_docs_dir)
    if not paths:
        return pd.DataFrame(columns=["document_name", "page_number", "text", "char_count"])

    all_rows = []
    for p in paths:
        try:
            rows = extract_text_from_file(p)
            all_rows.extend(rows)
        except Exception as e:
            raise RuntimeError(f"Failed to extract {p}: {e}") from e
    return pd.DataFrame(all_rows)
