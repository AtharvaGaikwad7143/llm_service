from fastapi import APIRouter

from app.schemas import QueryRequest, QueryResponse
from app.services.rag_service import answer_question


router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    # Run the complete RAG pipeline:
    # question → retrieval → context → LLM → answer + sources
    result = await answer_question(request.question)

    return QueryResponse(**result)