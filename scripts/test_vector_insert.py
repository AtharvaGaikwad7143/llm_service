import asyncio

from app.services.embeddings import embed_text
from app.repositories.vector_repository import insert_chunk

async def main():

    text = "Redis is an in-memory data store."
    embedding = embed_text(text)

    chunk_id = await insert_chunk(
        document_id=1,
        chunk_text=text,
        embedding=embedding,
        metadata={
            "topic": "redis",
        },
    )

    print("Inserted chunk ID:", chunk_id)


if __name__ == "__main__":
    asyncio.run(main())