from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_parser import extract_pages_from_pdf
from app.repositories.document_repository import create_document
from app.repositories.vector_repository import insert_chunk
from app.services.embeddings import embed_text


async def ingest_document(
    pdf_path: str,
    filename: str,
) -> dict:
    """
    Complete document ingestion pipeline.

    PDF
      ↓
    page extraction
      ↓
    token-aware chunking
      ↓
    embeddings
      ↓
    PostgreSQL + pgvector
    """

    # Extract the PDF while preserving page numbers.
    pages = extract_pages_from_pdf(pdf_path)

    # Store the original document first.
    # The generated ID will be used by all chunks.
    full_text = "\n\n".join(
        page["text"]
        for page in pages
    )

    document_id = await create_document(
        filename=filename,
        content=full_text,
    )

    # Split pages into overlapping chunks.
    chunks = chunk_pages(
        pages,
        chunk_size=500,
        overlap=50,
    )

    # Process every chunk independently.
    for chunk in chunks:
        # Convert chunk text into a 384-dimensional embedding.
        embedding = embed_text(chunk["text"])

        # Store the vector together with useful source metadata.
        await insert_chunk(
            document_id=document_id,
            chunk_text=chunk["text"],
            embedding=embedding,
            metadata={
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
            },
        )

    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_created": len(chunks),
    }