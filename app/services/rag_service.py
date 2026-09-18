from app.services.embeddings import embed_text
from app.repositories.vector_repository import search_similar_chunks
from app.services.llm import llm_service


async def answer_question(question: str) -> dict:
    # Convert the user's question into the same vector space
    # used when we created document embeddings.
    query_embedding = embed_text(question)

    # Retrieve the most semantically similar chunks from pgvector.
    chunks = await search_similar_chunks(
        query_embedding=query_embedding,
        limit=5,
    )

    # Combine retrieved chunks into a single context for the LLM.
    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Document {chunk['document_id']}, "
            f"Page {chunk['metadata'].get('page_number', 'unknown')}]\n"
            f"{chunk['chunk_text']}"
        )

    context = "\n\n".join(context_parts)

    # Tell the LLM to answer only from retrieved information.
    prompt = f"""
Answer the user's question using only the provided context.

If the context does not contain enough information to answer the question,
say that you don't have enough information.

Context:
{context}

Question:
{question}
"""

    # Generate the final answer using our existing LLM service.
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