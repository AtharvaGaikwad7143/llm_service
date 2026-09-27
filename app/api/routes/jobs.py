from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.repositories.job_repository import get_job


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.get("/{job_id}")
async def get_job_status(job_id: UUID):
    job = await get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return job