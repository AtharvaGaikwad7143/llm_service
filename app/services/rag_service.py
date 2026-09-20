import asyncio

from app.repositories.vector_repository import (
    search_keyword_chunks,
    search_similar_chunks,
)
from app.services.embeddings import embed_text
from app.services.llm import llm_service
from app.services.reranker import rerank_documents


def normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    if not scores:
        return {}

    values = list(scores.values())

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return {
            chunk_id: 1.0
            for chunk_id in scores
        }

    return {
        chunk_id: (score - minimum) / (maximum - minimum)
        for chunk_id, score in scores.items()
    }


async def hybrid_search(
    query: str,
    limit: int = 20,
) -> list[dict]:

    query_embedding = embed_text(query)

    # Run vector and keyword retrieval concurrently.
    vector_results, keyword_results = await asyncio.gather(
        search_similar_chunks(
            query_embedding=query_embedding,
            limit=limit,
        ),
        search_keyword_chunks(
            query=query,
            limit=limit,
        ),
    )

    vector_scores = {
        result["id"]: 1.0 - float(result["distance"])
        for result in vector_results
    }

    keyword_scores = {
        result["id"]: float(result["keyword_score"])
        for result in keyword_results
    }

    normalized_vector_scores = normalize_scores(
        vector_scores
    )

    normalized_keyword_scores = normalize_scores(
        keyword_scores
    )

    # Merge candidates from both retrieval systems.
    all_results = {}

    for result in vector_results + keyword_results:
        all_results[result["id"]] = result

    ranked_results = []

    for chunk_id, result in all_results.items():

        vector_score = normalized_vector_scores.get(
            chunk_id,
            0.0,
        )

        keyword_score = normalized_keyword_scores.get(
            chunk_id,
            0.0,
        )

        hybrid_score = (
            0.7 * vector_score
            + 0.3 * keyword_score
        )

        ranked_results.append(
            {
                "id": chunk_id,
                "document_id": result["document_id"],
                "chunk_text": result["chunk_text"],
                "metadata": result["metadata"],
                "vector_score": vector_score,
                "keyword_score": keyword_score,
                "hybrid_score": hybrid_score,
            }
        )

    ranked_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    return ranked_results[:limit]


async def answer_question(question: str) -> dict:

    # First stage: retrieve a larger candidate pool.
    candidates = await hybrid_search(
        query=question,
        limit=20,
    )

    # Second stage: use the cross-encoder to select
    # the most relevant chunks.
    chunks = rerank_documents(
        query=question,
        documents=candidates,
        top_k=5,
    )

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Document {chunk['document_id']}, "
            f"Page {chunk['metadata'].get('page_number', 'unknown')}]\n"
            f"{chunk['chunk_text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
Answer the user's question using only the provided context.

If the context does not contain enough information to answer the question,
say that you don't have enough information.

Context:
{context}

Question:
{question}
"""

    answer = await llm_service.generate(prompt)

    return {
        "answer": answer,
        "sources": [
            {
                "document_id": chunk["document_id"],
                "metadata": chunk["metadata"],
            }
            for chunk in chunks
        ],
    }