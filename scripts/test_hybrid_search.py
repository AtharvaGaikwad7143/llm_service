import asyncio

from app.services.rag_service import hybrid_search


async def main():
    results = await hybrid_search(
        query="What is Redis used for caching?",
        limit=5,
    )

    for result in results:
        print(
            f"document={result['document_id']} "
            f"vector={result['vector_score']:.4f} "
            f"keyword={result['keyword_score']:.4f} "
            f"hybrid={result['hybrid_score']:.4f}"
        )

        print(result["chunk_text"])
        print()


if __name__ == "__main__":
    asyncio.run(main())

