from sqlalchemy import text

from app.db.database import AsyncSessionLocal


async def create_document(
    filename: str,
    content: str,
) -> int:
    
    async with AsyncSessionLocal() as session:
        query = text(
            """
            INSERT INTO documents (
                filename,
                content
            )
            VALUES (
                :filename,
                :content
            )
            RETURNING id
            """
        )

        result = await session.execute(
            query,
            {
                "filename": filename,
                "content": content,
            },
        )

        await session.commit()

        return result.scalar_one()


async def get_document(
    document_id: int,
) -> dict | None:

    async with AsyncSessionLocal() as session:
        query = text(
            """
            SELECT
                id,
                filename,
                content,
                created_at
            FROM documents
            WHERE id = :document_id
            """
        )

        result = await session.execute(
            query,
            {
                "document_id": document_id,
            },
        )

        row = result.mappings().one_or_none()

        if row is None:
            return None

        return dict(row)