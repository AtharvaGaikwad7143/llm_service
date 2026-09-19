import asyncio
from app.repositories.vector_repository import (
    search_keyword_chunks,
    search_similar_chunks,
)
from app.services.embeddings import embed_text
from app.services.llm import llm_service


def normalize_scores(scores: dict[int, float]) -> dict[int, float]:
    """
    Normalize scores to the range [0, 1] using min-max normalization.

    This allows vector and keyword scores, which have different
    score distributions, to be combined more meaningfully.
    """

    if not scores:
        return {}

    values = list(scores.values())

    minimum = min(values)
    maximum = max(values)

    # If every score is identical, there is no useful difference
    # between the results.
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
    limit: int = 5,
) -> list[dict]:
    """
    Retrieve documents using both:

    1. Semantic vector search
    2. PostgreSQL keyword search

    Then combine both signals into a hybrid ranking.
    """

    # One embedding is enough for the vector search.
    query_embedding = embed_text(query)

    # Run both retrieval systems concurrently.
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

    # Convert cosine distance into similarity.
    #
    # pgvector:
    # lower distance = better
    #
    # Therefore:
    # similarity = 1 - distance
    vector_scores = {
        result["id"]: 1.0 - float(result["distance"])
        for result in vector_results
    }

    # PostgreSQL:
    # higher ts_rank = better
    keyword_scores = {
        result["id"]: float(result["keyword_score"])
        for result in keyword_results
    }

    # Normalize both scoring systems independently.
    normalized_vector_scores = normalize_scores(vector_scores)
    normalized_keyword_scores = normalize_scores(keyword_scores)

    # Keep every chunk returned by either retrieval method.
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

        # Weighted hybrid ranking.
        #
        # Semantic meaning gets more weight.
        # Exact keyword matching provides an additional signal.
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

    # Highest hybrid score first.
    ranked_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    return ranked_results[:limit]


async def answer_question(question: str) -> dict:
    """
    Complete RAG pipeline:

    Question
        ↓
    Hybrid Retrieval
        ↓
    Context
        ↓
    Gemini
        ↓
    Answer + Sources
    """

    chunks = await hybrid_search(
        query=question,
        limit=5,
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
