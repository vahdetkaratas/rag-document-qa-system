"""API request/response schemas. RAG_SYSTEM_DESIGN §7, IMPLEMENTATION_REFERENCE §8."""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    """Body for POST /ask: one natural-language question."""

    question: str = Field(
        ...,
        min_length=1,
        description=(
            "Natural-language question. The API embeds this query, retrieves the most similar "
            "document chunks from the FAISS index, and asks the LLM to answer using only that context."
        ),
        examples=[
            "What is the P1 incident response time?",
            "What does the refund policy say about annual subscriptions?",
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"question": "What are the P1 incident response times?"},
            ]
        }
    )


class SourceCitation(BaseModel):
    """One retrieved passage cited for the answer."""

    document: str = Field(
        ...,
        description="Source file name (e.g. policy or manual filename).",
        examples=["incident_response_manual.txt"],
    )
    page: int = Field(
        ...,
        description="1-based page number within that document (as recorded at chunking time).",
        examples=[1],
    )
    chunk_id: str = Field(
        ...,
        description="Stable chunk identifier from the chunking pipeline (traceability).",
        examples=["incident_response_manual_p1_0"],
    )


class AskResponse(BaseModel):
    """Answer plus citations; may include raw retrieved chunks for inspection."""

    answer: str = Field(
        ...,
        description=(
            "Model answer grounded in retrieved context. If retrieval is weak (see server "
            "`RETRIEVAL_MIN_SCORE`) or the LLM refuses, this may be a short fallback message."
        ),
    )
    sources: list[SourceCitation] = Field(
        ...,
        description="Citations for chunks used as context (document, page, chunk_id).",
    )
    retrieved_chunks: list[dict[str, Any]] | None = Field(
        default=None,
        description=(
            "Optional diagnostic payload: full retrieved rows (text, scores, metadata) for this request. "
            "Useful in Swagger or debugging to see what the model was shown. Shape matches internal chunk dicts."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "answer": "For P1 incidents, response is within 15 minutes.",
                    "sources": [
                        {
                            "document": "incident_response_manual.txt",
                            "page": 1,
                            "chunk_id": "incident_response_manual_p1_0",
                        }
                    ],
                    "retrieved_chunks": None,
                }
            ]
        }
    )
