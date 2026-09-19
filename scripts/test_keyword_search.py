
import asyncio

from app.repositories.vector_repository import search_keyword_chunks


async def main():
    results = await search_keyword_chunks(
        query="Redis caching",
        limit=5,
    )

    for result in results:
        print(
            f"document={result['document_id']} "
            f"score={result['keyword_score']:.4f}"
        )
        print(result["chunk_text"])
        print()


if __name__ == "__main__":
    asyncio.run(main())

