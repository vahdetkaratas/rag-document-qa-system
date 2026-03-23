"""
End-to-end QA: question -> retrieve -> build prompt -> LLM -> answer + sources. RAG_SYSTEM_DESIGN §5.
RETRIEVAL_MIN_SCORE: if best chunk score is below this, LLM is not called (reduces hallucination risk).
"""
import logging
import os

from src.retrieval.retrieve import retrieve_top_k

logger = logging.getLogger(__name__)
from src.generation.prompt_builder import build_qa_prompt
from src.generation.answer_generator import generate_answer

FALLBACK_ANSWER = "I could not find enough supporting evidence in the documents to answer this question."


def _retrieval_min_score() -> float:
    raw = (os.getenv("RETRIEVAL_MIN_SCORE") or "").strip()
    if not raw:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _chunks_to_sources(chunks: list[dict]) -> list[dict]:
    """Format retrieved chunks as source citations: document, page, chunk_id."""
    return [
        {
            "document": c.get("document_name", ""),
            "page": int(c.get("page_number", 0)),
            "chunk_id": c.get("chunk_id", ""),
        }
        for c in chunks
    ]


def run_qa(
    question: str,
    top_k: int = 5,
    use_llm: bool = True,
):
    """
    Run full QA pipeline: retrieve top_k chunks, build prompt, generate answer (if use_llm), return answer + sources.
    If use_llm=False, returns empty answer and only sources (for testing retrieval).
    Returns dict: answer, sources, retrieved_chunks (optional).
    """
    question = (question or "").strip()
    if not question:
        return {
            "answer": "Please provide a question.",
            "sources": [],
            "retrieved_chunks": [],
        }

    chunks = retrieve_top_k(question, top_k=top_k)
    sources = _chunks_to_sources(chunks)

    min_score = _retrieval_min_score()
    if use_llm and min_score > 0 and chunks:
        best = max(float(c.get("score") or 0.0) for c in chunks)
        if best < min_score:
            logger.warning(
                "QA: RETRIEVAL_MIN_SCORE blocked LLM call (best_score=%.4f, min_score=%.4f, top_k=%s)",
                best,
                min_score,
                len(chunks),
            )
            return {
                "answer": FALLBACK_ANSWER,
                "sources": sources,
                "retrieved_chunks": chunks,
            }

    if not use_llm:
        return {
            "answer": "",
            "sources": sources,
            "retrieved_chunks": chunks,
        }

    prompt = build_qa_prompt(question, chunks)
    try:
        answer = generate_answer(prompt)
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise
        logger.warning("QA: generate_answer raised ValueError; using fallback: %s", e)
        answer = FALLBACK_ANSWER
    except Exception as e:
        logger.warning("LLM generation failed; using fallback (type=%s)", type(e).__name__)
        answer = FALLBACK_ANSWER

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": chunks,
    }
