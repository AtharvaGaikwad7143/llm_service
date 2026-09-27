from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import text

from app.db.database import AsyncSessionLocal


async def create_job(job_id: UUID) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                """
                INSERT INTO jobs (id, status)
                VALUES (:job_id, 'PENDING')
                """
            ),
            {
                "job_id": job_id,
            },
        )

        await session.commit()


async def mark_job_processing(job_id: UUID) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                """
                UPDATE jobs
                SET status = 'PROCESSING',
                    started_at = :started_at
                WHERE id = :job_id
                """
            ),
            {
                "job_id": job_id,
                "started_at": datetime.now(timezone.utc),
            },
        )

        await session.commit()


async def mark_job_completed(
    job_id: UUID,
    document_id: int,
) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                """
                UPDATE jobs
                SET status = 'COMPLETED',
                    document_id = :document_id,
                    completed_at = :completed_at
                WHERE id = :job_id
                """
            ),
            {
                "job_id": job_id,
                "document_id": document_id,
                "completed_at": datetime.now(timezone.utc),
            },
        )

        await session.commit()


async def mark_job_failed(
    job_id: UUID,
    error: str = "Document processing failed.",
) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                """
                UPDATE jobs
                SET status = 'FAILED',
                    completed_at = :completed_at,
                    error = :error
                WHERE id = :job_id
                """
            ),
            {
                "job_id": job_id,
                "completed_at": datetime.now(timezone.utc),
                "error": error,
            },
        )

        await session.commit()


async def get_job(job_id: UUID) -> dict | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(
                """
                SELECT
                    id,
                    document_id,
                    status,
                    created_at,
                    started_at,
                    completed_at,
                    error
                FROM jobs
                WHERE id = :job_id
                """
            ),
            {"job_id": job_id},
        )

        row = result.mappings().first()

        if row is None:
            return None

        return dict(row)