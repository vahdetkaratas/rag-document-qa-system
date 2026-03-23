"""
List supported document paths from raw_docs. RAG_SYSTEM_DESIGN §3, IMPLEMENTATION_REFERENCE §11.
"""
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def list_document_paths(raw_docs_dir: str | Path) -> list[Path]:
    """
    Return list of file paths in raw_docs_dir with supported extensions (.pdf, .txt, .md).
    """
    raw_docs_dir = Path(raw_docs_dir)
    if not raw_docs_dir.exists():
        return []
    paths = []
    for f in raw_docs_dir.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            paths.append(f)
    return sorted(paths)
