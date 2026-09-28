from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_parser import extract_pages_from_pdf
from app.repositories.document_repository import create_document
from app.repositories.vector_repository import insert_chunk
from app.services.embeddings import embed_text


async def ingest_document(
    pdf_path: str,
    filename: str,
    content_hash: str,
) -> dict:
    """
    Complete document ingestion pipeline.

    PDF
      ↓
    page extraction
      ↓
    token-aware chunking
      ↓
    document creation / duplicate detection
      ↓
    embeddings
      ↓
    PostgreSQL + pgvector
    """

    pages = extract_pages_from_pdf(pdf_path)

    full_text = "\n\n".join(
        page["text"]
        for page in pages
    )

    document_id, created = await create_document(
        filename=filename,
        content=full_text,
        content_hash=content_hash,
    )

    chunks = chunk_pages(
        pages,
        chunk_size=500,
        overlap=50,
    )

    chunks_created = 0

    for chunk in chunks:
        embedding = embed_text(chunk["text"])

        await insert_chunk(
            document_id=document_id,
            chunk_text=chunk["text"],
            embedding=embedding,
            metadata={
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
            },
        )

        chunks_created += 1

    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_created": chunks_created,
        "duplicate": not created,
    }