"""QA pipeline: retrieval score threshold (RETRIEVAL_MIN_SCORE)."""
import pytest

from src.pipeline import qa_pipeline as qp


def test_retrieval_min_score_blocks_llm(monkeypatch):
    monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.99")

    def fake_retrieve(question, top_k=5, index_path=None, metadata_path=None):
        return [
            {
                "document_name": "doc.txt",
                "page_number": 1,
                "text": "Some text.",
                "chunk_id": "c1",
                "score": 0.2,
            }
        ]

    monkeypatch.setattr(qp, "retrieve_top_k", fake_retrieve)
    calls = []

    def no_llm(prompt):
        calls.append(prompt)
        return "BAD"

    monkeypatch.setattr(qp, "generate_answer", no_llm)
    out = qp.run_qa("anything?", use_llm=True)
    assert qp.FALLBACK_ANSWER in out["answer"] or "evidence" in out["answer"].lower()
    assert calls == []


def test_retrieval_min_score_disabled_calls_llm(monkeypatch):
    monkeypatch.delenv("RETRIEVAL_MIN_SCORE", raising=False)

    def fake_retrieve(question, top_k=5, index_path=None, metadata_path=None):
        return [
            {
                "document_name": "doc.txt",
                "page_number": 1,
                "text": "Answer is forty-two.",
                "chunk_id": "c1",
                "score": 0.2,
            }
        ]

    monkeypatch.setattr(qp, "retrieve_top_k", fake_retrieve)
    monkeypatch.setattr(qp, "generate_answer", lambda p: "forty-two")
    out = qp.run_qa("what?", use_llm=True)
    assert "forty-two" in out["answer"]
