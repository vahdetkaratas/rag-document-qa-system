"""
Retrieval pipeline: question -> top-k chunks. Thin wrapper over retrieve.retrieve_top_k. MILESTONES M3.
"""
from src.retrieval.retrieve import retrieve_top_k


def run_retrieval(question: str, top_k: int = 5, **kwargs):
    """
    Run retrieval for a question. Returns list of dicts (chunk metadata + score).
    """
    return retrieve_top_k(question, top_k=top_k, **kwargs)
