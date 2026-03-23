"""Tests for prompt builder. LLM call skipped without API key."""
import pytest
from src.generation.prompt_builder import build_qa_prompt

def test_build_qa_prompt_with_context():
    chunks = [{"document_name": "doc.pdf", "page_number": 1, "text": "Cancellation requires 14 days notice."}]
    prompt = build_qa_prompt("What is the cancellation policy?", chunks)
    assert "Cancellation" in prompt
    assert "What is the cancellation policy?" in prompt

def test_build_qa_prompt_empty_context():
    prompt = build_qa_prompt("Any question?", [])
    assert "not find enough" in prompt or "supporting evidence" in prompt
