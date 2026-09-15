import asyncio

from app.repositories.vector_repository import search_similar_chunks
from app.services.embeddings import embed_text


async def main():

    query = "What is caching?"

    # Convert the user's query into a 384-dimensional vector.
    query_embedding = embed_text(query)

    results = await search_similar_chunks(
        query_embedding=query_embedding,
        limit=5,
        metadata_filter={"topic": "redis"},
    )

    print(f"\nQuery: {query}")
    print("Filter: topic=redis\n")

    for result in results:
        print(f"Distance: {result['distance']:.4f}")
        print(f"Chunk: {result['chunk_text']}")
        print(f"Metadata: {result['metadata']}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())