"""
Chunking: split text into chunks with overlap. RAG_SYSTEM_DESIGN §3, IMPLEMENTATION_REFERENCE §3, §12.
chunk_size=1200, chunk_overlap=200. Metadata: chunk_id, document_name, page_number, chunk_index_within_page, text, char_count, start_char, end_char.
"""
from pathlib import Path

import pandas as pd

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def _make_chunk_id(document_name: str, page_number: int, chunk_index: int) -> str:
    """Generate chunk_id e.g. refund_policy_p3_c2."""
    base = Path(document_name).stem.replace(" ", "_").replace(".", "_")
    return f"{base}_p{page_number}_c{chunk_index}"


def split_text_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, int, int]]:
    """
    Split text into overlapping chunks. Returns list of (chunk_text, start_char, end_char).
    """
    if not text or len(text.strip()) == 0:
        return []
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        if chunk_text.strip():
            chunks.append((chunk_text, start, end))
        start = end - chunk_overlap if end < len(text) else len(text)
    return chunks


def build_chunk_dataframe(extraction_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build chunk DataFrame from extraction DataFrame (columns: document_name, page_number, text, char_count).
    Output columns: chunk_id, document_name, page_number, chunk_index_within_page, text, char_count, start_char, end_char.
    """
    rows = []
    for _, row in extraction_df.iterrows():
        doc_name = row["document_name"]
        page = int(row["page_number"])
        text = row["text"] if pd.notna(row["text"]) else ""
        for idx, (chunk_text, start_char, end_char) in enumerate(
            split_text_into_chunks(text)
        ):
            chunk_id = _make_chunk_id(doc_name, page, idx)
            rows.append({
                "chunk_id": chunk_id,
                "document_name": doc_name,
                "page_number": page,
                "chunk_index_within_page": idx,
                "text": chunk_text,
                "char_count": len(chunk_text),
                "start_char": start_char,
                "end_char": end_char,
            })
    return pd.DataFrame(rows)
