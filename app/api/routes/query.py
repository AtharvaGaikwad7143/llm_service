import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import QueryRequest, QueryResponse
from app.services.rag_service import answer_question, stream_answer


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Run the complete RAG pipeline and return a structured response.

    Flow:
    question → retrieval → reranking → context → LLM
    → answer + sources + confidence
    """
    result = await answer_question(request.question)

    return QueryResponse(**result)


@router.post("/stream")
async def stream_query(request: QueryRequest):
    """
    Stream the RAG answer using Server-Sent Events (SSE).

    Flow:
    question → retrieval → reranking → context
    → Gemini streaming → SSE token events
    """

    async def event_generator():
        try:
            async for chunk in stream_answer(request.question):
                yield f"data: {json.dumps({
                    'type': 'token',
                    'content': chunk,
                })}\n\n"

            # Tell the client that generation completed successfully.
            yield f"data: {json.dumps({
                'type': 'done',
            })}\n\n"

        except Exception:
            # Once an SSE response has started, we cannot change the
            # HTTP status code. Therefore, send the error as an SSE event.
            logger.exception("Streaming RAG request failed")

            yield f"data: {json.dumps({
                'type': 'error',
                'message': 'Unable to generate response right now.',
            })}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )