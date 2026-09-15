import asyncio

from app.repositories.vector_repository import insert_chunk
from app.services.embeddings import embed_text


DOCUMENTS = [
    {
        "document_id": 1,
        "text": "Redis is an in-memory data store commonly used for caching and fast key-value operations.",
        "metadata": {"topic": "redis"},
    },
    {
        "document_id": 2,
        "text": "PostgreSQL is a relational database management system that stores structured data using tables and SQL.",
        "metadata": {"topic": "postgresql"},
    },
    {
        "document_id": 3,
        "text": "Python is a high-level programming language commonly used for backend development, automation, and data science.",
        "metadata": {"topic": "python"},
    },
    {
        "document_id": 4,
        "text": "Docker packages applications and their dependencies into containers so they can run consistently across environments.",
        "metadata": {"topic": "docker"},
    },
    {
        "document_id": 5,
        "text": "Paris is the capital city of France and is famous for landmarks such as the Eiffel Tower.",
        "metadata": {"topic": "travel"},
    },
]


async def main():

    for document in DOCUMENTS:

        # Current chunk ka text.
        text = document["text"]

        # Same embedding model
        embedding = embed_text(text)

        # Chunk + embedding database save.
        chunk_id = await insert_chunk(
            document_id=document["document_id"],
            chunk_text=text,
            embedding=embedding,
            metadata=document["metadata"],
        )

        print(
            f"Inserted chunk {chunk_id} "
            f"for document {document['document_id']}"
        )


if __name__ == "__main__":
    asyncio.run(main())