"""
Run chunking on extracted_documents.csv and save chunked_documents.csv. MILESTONES M2.
"""
from pathlib import Path

import pandas as pd

from src.ingestion.chunk_documents import build_chunk_dataframe
from src.utils.file_helpers import ensure_dir

from src.config import CHUNK_OUTPUT, EXTRACTION_OUTPUT as CHUNK_INPUT


def run_chunking(
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    Read extraction CSV, chunk, save to output_path. Returns path to written CSV.
    """
    input_path = Path(input_path or CHUNK_INPUT)
    output_path = Path(output_path or CHUNK_OUTPUT)
    ensure_dir(output_path.parent)

    if not input_path.exists():
        raise FileNotFoundError(f"Extraction not found: {input_path}. Run run_extraction first.")
    df = pd.read_csv(input_path)
    chunk_df = build_chunk_dataframe(df)
    if chunk_df.empty:
        raise ValueError("No chunks produced. Check extraction data.")
    chunk_df.to_csv(output_path, index=False)
    print(f"Chunked {len(chunk_df)} chunks to {output_path}")
    return output_path


if __name__ == "__main__":
    run_chunking()
