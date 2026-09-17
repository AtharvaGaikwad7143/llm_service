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