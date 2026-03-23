"""
Run extraction and save to artifacts/extraction/extracted_documents.csv. MILESTONES M1.
"""
from pathlib import Path

from src.ingestion.extract_text import extract_all
from src.utils.file_helpers import ensure_dir

from src.config import EXTRACTION_OUTPUT, RAW_DOCS_DIR


def run_extraction(
    raw_docs_dir: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    Extract text from all supported docs in raw_docs_dir; save CSV to output_path.
    Returns path to written CSV.
    """
    raw_docs_dir = Path(raw_docs_dir or RAW_DOCS_DIR)
    output_path = Path(output_path or EXTRACTION_OUTPUT)
    ensure_dir(output_path.parent)

    df = extract_all(raw_docs_dir)
    if df.empty:
        raise FileNotFoundError(f"No supported documents found in {raw_docs_dir}")
    df.to_csv(output_path, index=False)
    print(f"Extracted {len(df)} rows to {output_path}")
    return output_path


if __name__ == "__main__":
    run_extraction()
