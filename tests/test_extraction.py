"""
Tests for document loading and text extraction. IMPLEMENTATION_REFERENCE §1, MILESTONES M1.
"""
from pathlib import Path

import pandas as pd
import pytest

from src.ingestion.load_documents import list_document_paths, SUPPORTED_EXTENSIONS
from src.ingestion.extract_text import extract_text_from_file, extract_all

from src.config import RAW_DOCS_DIR as RAW_DOCS


def test_supported_extensions():
    """SUPPORTED_EXTENSIONS includes .pdf, .txt, .md."""
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".txt" in SUPPORTED_EXTENSIONS
    assert ".md" in SUPPORTED_EXTENSIONS


def test_list_document_paths_returns_paths():
    """list_document_paths returns list of Path for supported files in raw_docs."""
    if not RAW_DOCS.exists():
        pytest.skip("data/raw_docs not found")
    paths = list_document_paths(RAW_DOCS)
    assert isinstance(paths, list)
    for p in paths:
        assert isinstance(p, Path)
        assert p.suffix.lower() in SUPPORTED_EXTENSIONS


def test_extract_text_from_file_txt():
    """extract_text_from_file for .txt returns one row with document_name, page_number, text, char_count."""
    sample = RAW_DOCS / "customer_onboarding_policy.txt"
    if not sample.exists():
        pytest.skip("customer_onboarding_policy.txt not found")
    rows = extract_text_from_file(sample)
    assert len(rows) >= 1
    assert rows[0]["document_name"] == "customer_onboarding_policy.txt"
    assert rows[0]["page_number"] == 1
    assert "text" in rows[0]
    assert "char_count" in rows[0]
    assert "Onboarding" in rows[0]["text"] or "onboarding" in rows[0]["text"]


def test_extract_all_returns_dataframe():
    """extract_all returns DataFrame with columns document_name, page_number, text, char_count."""
    if not RAW_DOCS.exists():
        pytest.skip("data/raw_docs not found")
    df = extract_all(RAW_DOCS)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["document_name", "page_number", "text", "char_count"]
    assert len(df) >= 1
