"""
Answer evaluation: run QA for each eval question, optionally compare to expected. RAG_SYSTEM_DESIGN §6.
Saves results to artifacts/eval_results. Correctness/Groundedness can be manual or heuristic.
"""
from pathlib import Path

import pandas as pd

from src.pipeline.qa_pipeline import run_qa

from src.config import EVAL_QUESTIONS_PATH, EVAL_RESULTS_DIR


def evaluate_answers_batch(
    eval_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    use_llm: bool = True,
) -> pd.DataFrame:
    """
    Load eval questions, run QA for each, return DataFrame with question, answer, sources, expected_document.
    Does not require OPENAI_API_KEY if use_llm=False (retrieval-only).
    """
    eval_path = Path(eval_path or EVAL_QUESTIONS_PATH)
    output_dir = Path(output_dir or EVAL_RESULTS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not eval_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(eval_path)
    if "question" not in df.columns:
        return pd.DataFrame()

    rows = []
    for _, row in df.iterrows():
        q = row["question"]
        out = run_qa(q, top_k=5, use_llm=use_llm)
        rows.append({
            "question": q,
            "answer": out.get("answer", ""),
            "sources_count": len(out.get("sources", [])),
            "expected_document": row.get("expected_document", ""),
        })
    result_df = pd.DataFrame(rows)
    result_df.to_csv(output_dir / "answer_eval.csv", index=False)
    return result_df
