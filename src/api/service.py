"""API service: run_qa and format response."""
from src.pipeline.qa_pipeline import run_qa
from src.api.schemas import SourceCitation


def ask(question: str, top_k: int = 5, include_retrieved_chunks: bool = False) -> dict:
    """
    Run QA pipeline and return dict suitable for AskResponse.
    """
    result = run_qa(question, top_k=top_k, use_llm=True)
    sources = [SourceCitation(document=s["document"], page=s["page"], chunk_id=s["chunk_id"]) for s in result["sources"]]
    out = {
        "answer": result["answer"],
        "sources": [s.model_dump() for s in sources],
    }
    if include_retrieved_chunks:
        out["retrieved_chunks"] = result.get("retrieved_chunks", [])
    return out
