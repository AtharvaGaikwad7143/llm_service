from pydantic import BaseModel, Field


# -------------------------
# Day 1 — LLM generation
# -------------------------

class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str


# -------------------------
# Day 1 — Structured extraction
# -------------------------

class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    title: str
    summary: str
    keywords: list[str]


# -------------------------
# Day 5 — Semantic search
# -------------------------

class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language search query.",
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return.",
    )


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_text: str
    similarity: float
    metadata: dict


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Question to ask about the uploaded documents."
    )


class Source(BaseModel):
    document_id: int
    metadata: dict


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class RAGResponse(BaseModel):
    answer: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class RAGEvaluation(BaseModel):
    relevance: float = Field(ge=0.0, le=1.0)
    faithfulness: float = Field(ge=0.0, le=1.0)
    correctness: float = Field(ge=0.0, le=1.0)
    reason: str