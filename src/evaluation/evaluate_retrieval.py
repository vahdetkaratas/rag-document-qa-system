"""
Retrieval evaluation: top-1, top-3, top-5 hit rate. RAG_SYSTEM_DESIGN §6.
eval_questions.csv: question, expected_document. For each question we retrieve and check if expected_document in top-k.
"""
from pathlib import Path

import pandas as pd

from src.retrieval.retrieve import retrieve_top_k

from src.config import EVAL_QUESTIONS_PATH


def _doc_in_results(expected: str, doc_names: list[str], k: int) -> bool:
    """True if expected document appears in top-k (exact or filename match)."""
    top = doc_names[:k]
    exp = expected.strip()
    if not exp:
        return False
    for name in top:
        n = (name or "").strip()
        if not n:
            continue
        if exp == n or exp in n or n in exp:
            return True
    return False


def evaluate_retrieval(
    eval_path: str | Path | None = None,
    top_k_list: list[int] | None = None,
) -> dict:
    """
    Load eval set, run retrieval for each question, compute hit@1, hit@3, hit@5.
    Returns dict with hit_rates and per-question results.
    """
    eval_path = Path(eval_path or EVAL_QUESTIONS_PATH)
    top_k_list = top_k_list or [1, 3, 5]
    if not eval_path.exists():
        return {"error": f"Eval file not found: {eval_path}", "hit_rates": {}}

    df = pd.read_csv(eval_path)
    if "question" not in df.columns or "expected_document" not in df.columns:
        return {"error": "eval_questions.csv must have question, expected_document", "hit_rates": {}}

    max_k = max(top_k_list)
    hit_counts = {k: 0 for k in top_k_list}
    n = len(df)

    for _, row in df.iterrows():
        q = row["question"]
        expected = str(row["expected_document"]).strip()
        if not expected:
            continue
        results = retrieve_top_k(q, top_k=max_k)
        doc_names = [r.get("document_name", "") for r in results]
        # Each Hit@k independent: if correct doc at rank 2, both Hit@3 and Hit@5 increment (no break).
        for k in top_k_list:
            if _doc_in_results(expected, doc_names, k):
                hit_counts[k] += 1

    hit_rates = {f"hit@{k}": hit_counts[k] / n if n else 0 for k in top_k_list}
    return {"hit_rates": hit_rates, "n_questions": n, "hit_counts": hit_counts}
