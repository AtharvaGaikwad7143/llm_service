from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.tasks import process_document
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas import SearchRequest, SearchResponse
from app.repositories.vector_repository import search_similar_chunks
from app.services.embeddings import embed_text
from app.repositories.document_repository import get_document


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


UPLOAD_DIR = Path("/app/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4()}.pdf"
    pdf_path = UPLOAD_DIR / stored_filename

    total_size = 0

    try:
        with pdf_path.open("wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    pdf_path.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=413,
                        detail="PDF file is too large. Maximum size is 10 MB.",
                    )

                output_file.write(chunk)

        task = process_document.delay(
            str(pdf_path),
            file.filename or "unknown.pdf",
        )

        return {
            "task_id": task.id,
            "filename": file.filename or "unknown.pdf",
            "status": "queued",
        }

    except HTTPException:
        raise

    except Exception:
        pdf_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to queue document for processing.",
        )

    finally:
        await file.close()


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