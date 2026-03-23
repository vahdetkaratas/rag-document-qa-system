"""Retrieval evaluation logic (Hit@k) — no FAISS required."""
import importlib

import pandas as pd
import pytest

# Module name same as function (evaluate_retrieval); patch via module reference.
_er = importlib.import_module("src.evaluation.evaluate_retrieval")
evaluate_retrieval = _er.evaluate_retrieval
_doc_in_results = _er._doc_in_results


def test_doc_in_results_exact():
    assert _doc_in_results("a.txt", ["b.txt", "a.txt"], k=3) is True
    assert _doc_in_results("a.txt", ["b.txt", "a.txt"], k=1) is False


def test_hit_at_k_independent(monkeypatch, tmp_path):
    """
    Correct doc at rank 2: Hit@1=0, Hit@3=1, Hit@5=1 for that question.
    Old bug: break after first k hid Hit@5.
    """
    def fake_retrieve(question, top_k=5, index_path=None, metadata_path=None):
        return [
            {"document_name": "wrong_doc.txt", "text": "x", "chunk_id": "1"},
            {"document_name": "target_doc.txt", "text": "y", "chunk_id": "2"},
        ][:top_k]

    monkeypatch.setattr(_er, "retrieve_top_k", fake_retrieve)
    csv = tmp_path / "eval.csv"
    csv.write_text(
        "question,expected_document\n"
        "q1?,target_doc.txt\n",
        encoding="utf-8",
    )
    out = evaluate_retrieval(eval_path=csv, top_k_list=[1, 3, 5])
    assert out["n_questions"] == 1
    assert out["hit_rates"]["hit@1"] == 0.0
    assert out["hit_rates"]["hit@3"] == 1.0
    assert out["hit_rates"]["hit@5"] == 1.0


def test_hit_at_k_all_three_questions(monkeypatch, tmp_path):
    """Two questions have correct doc at rank 1; third at rank 2 → Hit@1=2/3, Hit@3=1."""

    def fake_retrieve(question, top_k=5, index_path=None, metadata_path=None):
        q = (question or "").lower()
        if "third" in q:
            return [
                {"document_name": "other.txt", "text": "", "chunk_id": "0"},
                {"document_name": "doc_c.txt", "text": "", "chunk_id": "1"},
            ]
        if "second" in q:
            return [{"document_name": "doc_b.txt", "text": "", "chunk_id": "0"}]
        return [{"document_name": "doc_a.txt", "text": "", "chunk_id": "0"}]

    monkeypatch.setattr(_er, "retrieve_top_k", fake_retrieve)
    csv = tmp_path / "eval.csv"
    df = pd.DataFrame(
        {
            "question": ["first topic", "second topic", "third topic"],
            "expected_document": ["doc_a.txt", "doc_b.txt", "doc_c.txt"],
        }
    )
    df.to_csv(csv, index=False)

    out = evaluate_retrieval(eval_path=csv, top_k_list=[1, 3])
    n = 3
    # q1,q2 hit@1; q3 miss@1 hit@3
    assert out["hit_counts"][1] == 2
    assert out["hit_counts"][3] == 3
    assert out["hit_rates"]["hit@1"] == pytest.approx(2 / n)
    assert out["hit_rates"]["hit@3"] == 1.0
