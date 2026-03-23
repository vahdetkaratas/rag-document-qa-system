"""
LLM answer generation. Supports OpenAI and any OpenAI-compatible API (e.g. Ollama for free local use).
Fallback when context insufficient. IMPLEMENTATION_REFERENCE §2b.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_MODEL = "gpt-4o-mini"
FALLBACK_ANSWER = "I could not find enough supporting evidence in the documents to answer this question."


def _get_client():
    """
    Build OpenAI-compatible client. If OPENAI_API_BASE is set (e.g. Ollama), API key is optional.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package required. pip install openai")

    base_url = (os.getenv("OPENAI_API_BASE") or "").strip().rstrip("/")
    if base_url:
        # OpenAI-compatible endpoint (Ollama, OpenRouter, etc.): key often not required
        api_key = (os.getenv("OPENAI_API_KEY") or "ollama").strip()
        return OpenAI(api_key=api_key, base_url=base_url)
    # Standard OpenAI: key required
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not key or "your_key_here" in key:
        raise ValueError(
            "OPENAI_API_KEY not set. For OpenAI use a .env with OPENAI_API_KEY=sk-... "
            "For free local use set OPENAI_API_BASE=http://localhost:11434/v1 and OPENAI_MODEL=llama3.2 (see .env.example)."
        )
    return OpenAI(api_key=key)


def generate_answer(prompt: str, model: str | None = None) -> str:
    """
    Call OpenAI-compatible API for completion. Returns answer text.
    Uses OPENAI_MODEL from env when model not passed; OPENAI_API_BASE for alternate endpoint (e.g. Ollama).
    """
    client = _get_client()
    model = model or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2,
    )
    return (response.choices[0].message.content or "").strip()
