"""
Build prompt for LLM: context (retrieved chunks) + question. Grounded, fallback if insufficient. RAG_SYSTEM_DESIGN §5.
"""
from typing import Any


def build_qa_prompt(question: str, retrieved_chunks: list[dict], max_context_chars: int = 4000) -> str:
    """
    Build a single prompt string: instruction + context (from retrieved chunks) + question.
    If context is empty or too short, instruction asks to say "not enough evidence".
    """
    context_parts = []
    total_len = 0
    for c in retrieved_chunks:
        text = (c.get("text") or "").strip()
        if not text:
            continue
        doc = c.get("document_name", "unknown")
        page = c.get("page_number", "")
        context_parts.append(f"[Source: {doc}, page {page}]\n{text}")
        total_len += len(text)
        if total_len >= max_context_chars:
            break

    if not context_parts:
        return (
            "You are a helpful assistant that answers questions based only on the provided context. "
            "No relevant context was found. Reply briefly that you could not find enough supporting evidence to answer.\n\n"
            f"Question: {question}"
        )

    context = "\n\n---\n\n".join(context_parts)
    return (
        "You are a helpful assistant. Answer the question using ONLY the context below. "
        "Do not invent information. If the context does not contain enough information, "
        "say you could not find enough supporting evidence. Keep the answer concise.\n\n"
        "Context:\n"
        f"{context}\n\n"
        f"Question: {question}"
    )
