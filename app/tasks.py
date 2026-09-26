import asyncio
from pathlib import Path

from app.celery_app import celery_app
from app.services.document_service import ingest_document


@celery_app.task
def process_document(pdf_path: str, filename: str) -> dict:
    print(f"Processing document: {filename}")

    try:
        result = asyncio.run(
            ingest_document(
                pdf_path=pdf_path,
                filename=filename,
            )
        )

        print(f"Document processed successfully: {filename}")

        Path(pdf_path).unlink(missing_ok=True)

        return result

    except Exception as exc:
        print(f"Document processing failed: {filename}: {exc}")
        raise