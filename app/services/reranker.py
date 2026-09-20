from sentence_transformers import CrossEncoder


# Load the reranker once when the application starts.
# Loading it inside every request would be extremely expensive.
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_documents(
    query: str,
    documents: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Rerank retrieved documents using a cross-encoder.

    The cross-encoder receives the query and each document together
    and produces a relevance score.
    """

    if not documents:
        return []

    # Build query-document pairs for the cross-encoder.
    pairs = [
        [query, document["chunk_text"]]
        for document in documents
    ]

    # Calculate relevance scores.
    scores = reranker.predict(pairs)

    # Attach the reranker score to each document.
    ranked_documents = []

    for document, score in zip(documents, scores):
        ranked_documents.append(
            {
                **document,
                "rerank_score": float(score),
            }
        )

    # Highest relevance score first.
    ranked_documents.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return ranked_documents[:top_k]