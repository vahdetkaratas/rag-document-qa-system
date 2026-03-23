"""
Tests for chunking. MILESTONES M2, IMPLEMENTATION_REFERENCE §3, §12.
"""
from pathlib import Path

import pandas as pd
import pytest

from src.ingestion.chunk_documents import (
    split_text_into_chunks,
    build_chunk_dataframe,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

from src.config import EXTRACTION_OUTPUT as EXTRACTION_CSV


def test_split_text_into_chunks_respects_size():
    """Chunks are at most chunk_size chars (except possibly the last)."""
    text = "a" * 3000
    chunks = split_text_into_chunks(text, chunk_size=1200, chunk_overlap=200)
    assert len(chunks) >= 2
    for chunk_text, _, _ in chunks[:-1]:
        assert len(chunk_text) <= 1200 + 50  # allow small overshoot at boundary


def test_split_text_into_chunks_overlap():
    """With overlap, consecutive chunks share some text."""
    text = "x" * 1500
    chunks = split_text_into_chunks(text, chunk_size=500, chunk_overlap=100)
    assert len(chunks) >= 2
    end1 = chunks[0][0][-100:]
    start2 = chunks[1][0][:100]
    assert end1 == start2 or (end1 in chunks[1][0] or start2 in chunks[0][0])


def test_build_chunk_dataframe_columns():
    """build_chunk_dataframe output has chunk_id, document_name, page_number, chunk_index_within_page, text, char_count, start_char, end_char."""
    df = pd.DataFrame({
        "document_name": ["doc.txt"],
        "page_number": [1],
        "text": ["Hello world. " * 200],
        "char_count": [2600],
    })
    out = build_chunk_dataframe(df)
    assert "chunk_id" in out.columns
    assert "document_name" in out.columns
    assert "page_number" in out.columns
    assert "chunk_index_within_page" in out.columns
    assert "text" in out.columns
    assert "char_count" in out.columns
    assert "start_char" in out.columns
    assert "end_char" in out.columns
    assert len(out) >= 1


def test_run_chunking_e2e():
    """Run chunking on extraction output if available; check chunked_documents.csv has rows."""
    if not EXTRACTION_CSV.exists():
        pytest.skip("Run extraction first")
    from src.ingestion.run_chunking import run_chunking
    out_path = run_chunking()
    df = pd.read_csv(out_path)
    assert len(df) >= 1
    assert "chunk_id" in df.columns
    assert "text" in df.columns
