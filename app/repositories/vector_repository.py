import json

from sqlalchemy import text

from app.db.database import AsyncSessionLocal


async def insert_chunk(
    document_id: int,
    chunk_text: str,
    embedding: list[float],
    metadata: dict,
) -> int:
    """
    Store one document chunk and its embedding in PostgreSQL.
    """

    async with AsyncSessionLocal() as session:

        query = text(
            """
            INSERT INTO document_chunks (
                document_id,
                chunk_text,
                embedding,
                metadata
            )
            VALUES (
                :document_id,
                :chunk_text,
                CAST(:embedding AS vector),
                CAST(:metadata AS jsonb)
            )
            RETURNING id
            """
        )

        result = await session.execute(
            query,
            {
                "document_id": document_id,
                "chunk_text": chunk_text,
                "embedding": str(embedding),
                "metadata": json.dumps(metadata),
            },
        )

        await session.commit()

        return result.scalar_one()



async def search_similar_chunks(
    query_embedding: list[float],
    limit: int = 5,
    metadata_filter: dict | None = None,
) -> list[dict]:
    """
    Find the closest chunks to a query embedding.

    metadata_filter is optional.
    Example:
        {"topic": "redis"}
    """

    async with AsyncSessionLocal() as session:

        # Start with the basic vector similarity search.
        sql = """
            SELECT
                id,
                document_id,
                chunk_text,
                metadata,
                embedding <=> CAST(:query_embedding AS vector)
                    AS distance
            FROM document_chunks
        """

        params = {
            "query_embedding": str(query_embedding),
            "limit": limit,
        }

        # If a metadata filter was provided,
        # restrict the search to matching JSONB metadata.
        if metadata_filter is not None:
            sql += """
                WHERE metadata @> CAST(:metadata_filter AS jsonb)
            """

            params["metadata_filter"] = json.dumps(metadata_filter)

        # pgvector cosine distance:
        # lower distance = more similar.
        sql += """
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
        """

        result = await session.execute(
            text(sql),
            params,
        )

        rows = result.mappings().all()

        return [dict(row) for row in rows]