from sqlalchemy import text

from app.db.database import AsyncSessionLocal


async def create_document(
    filename: str,
    content: str,
    content_hash: str,
) -> tuple[int, bool]:
    async with AsyncSessionLocal() as session:
        query = text("""
            INSERT INTO documents (
                filename,
                content,
                content_hash
            )
            VALUES (
                :filename,
                :content,
                :content_hash
            )
            ON CONFLICT (content_hash)
            WHERE content_hash IS NOT NULL
            DO NOTHING
            RETURNING id
        """)

        result = await session.execute(
            query,
            {
                "filename": filename,
                "content": content,
                "content_hash": content_hash,
            },
        )

        document_id = result.scalar_one_or_none()

        # New document was inserted.
        if document_id is not None:
            await session.commit()
            return document_id, True

        # Document already exists.
        result = await session.execute(
            text("""
                SELECT id
                FROM documents
                WHERE content_hash = :content_hash
            """),
            {
                "content_hash": content_hash,
            },
        )

        document_id = result.scalar_one()

        await session.commit()

        return document_id, False


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