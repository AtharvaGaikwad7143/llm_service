from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.document_service import ingest_document
from app.schemas import SearchRequest, SearchResponse
from app.repositories.vector_repository import search_similar_chunks
from app.services.embeddings import embed_text
from app.repositories.document_repository import get_document
#from fastapi import Path

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Accept a PDF upload and send it through
    the document ingestion pipeline.
    """

    # We currently support PDF documents only.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Save the uploaded file temporarily.
    # The ingestion service expects a file path.
    with NamedTemporaryFile(
        suffix=".pdf",
        delete=False,
    ) as temp_file:
        temp_file.write(await file.read())
        temp_path = Path(temp_file.name)

    try:
        # Run the complete ingestion pipeline.
        result = await ingest_document(
            pdf_path=str(temp_path),
            filename=file.filename or "unknown.pdf",
        )

        return result

    finally:
        # Always delete the temporary PDF after processing.
        temp_path.unlink(missing_ok=True)


@router.post(
    "/search",
    response_model=SearchResponse,
)
async def search_documents(
    request: SearchRequest,
):
    """
    Perform semantic similarity search over
    stored document chunks.
    """

    # Convert the natural-language query into
    # the same 384-dimensional vector space used
    # when storing document chunk embeddings.
    query_embedding = embed_text(request.query)

    # Search pgvector for the nearest chunk vectors.
    results = await search_similar_chunks(
        query_embedding=query_embedding,
        limit=request.limit,
    )

    # Convert database rows into the public API format.
    formatted_results = [
        {
            "chunk_id": result["id"],
            "document_id": result["document_id"],
            "chunk_text": result["chunk_text"],
            "similarity": 1.0 - float(result["distance"]),
            "metadata": result["metadata"],
        }
        for result in results
    ]

    return SearchResponse(
        query=request.query,
        results=formatted_results,
    )


@router.get("/{document_id}")
async def get_document_by_id(
    document_id: int,
):
    """
    Return information about a stored document.
    """

    document = await get_document(document_id)

    # The requested document doesn't exist.
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document