import asyncio
from pathlib import Path
from uuid import UUID

from app.celery_app import celery_app
from app.repositories.job_repository import (
    mark_job_completed,
    mark_job_failed,
    mark_job_processing,
)
from app.services.document_service import ingest_document


async def _process_document(
    pdf_path: str,
    filename: str,
    job_id: str,
    content_hash: str,
) -> dict:
    job_uuid = UUID(job_id)

    await mark_job_processing(job_uuid)

    try:
        result = await ingest_document(
            pdf_path=pdf_path,
            filename=filename,
            content_hash=content_hash,
        )

        document_id = result["document_id"]

        await mark_job_completed(
            job_uuid,
            document_id,
        )

        print(
            f"Document processed successfully: "
            f"{filename} (document_id={document_id})"
        )

        Path(pdf_path).unlink(missing_ok=True)

        return result

    except Exception as exc:
        print(
            f"Document processing failed: "
            f"{filename}: {exc}"
        )

        try:
            await mark_job_failed(job_uuid)

        except Exception as state_error:
            print(
                f"Failed to update job state: "
                f"{state_error}"
            )

        raise


@celery_app.task
def process_document(
    pdf_path: str,
    filename: str,
    job_id: str,
    content_hash: str,
) -> dict:
    print(f"Processing document: {filename}")

    return asyncio.run(
        _process_document(
            pdf_path=pdf_path,
            filename=filename,
            job_id=job_id,
            content_hash=content_hash,
        )
    )