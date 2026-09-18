import json
import asyncio

from app.services.embeddings import embed_text
from app.repositories.vector_repository import search_similar_chunks


QUESTIONS_FILE = "scripts/rag_eval_questions.json"


async def evaluate_rag():
    # Load our 20 evaluation questions.
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    correct = 0

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        expected_document_id = item["expected_document_id"]

        # Convert the question into an embedding.
        query_embedding = embed_text(question)

        # Retrieve the top 5 most similar chunks from pgvector.
        results = await search_similar_chunks(
            query_embedding=query_embedding,
            limit=5,
        )

        # Extract document IDs returned by retrieval.
        retrieved_document_ids = [
            result["document_id"]
            for result in results
        ]

        # Recall@5:
        # Did the expected document appear anywhere in the top 5?
        is_correct = expected_document_id in retrieved_document_ids

        if is_correct:
            correct += 1

        status = "PASS" if is_correct else "FAIL"

        print(
            f"{index:02d}. {status} | "
            f"Expected: {expected_document_id} | "
            f"Retrieved: {retrieved_document_ids} | "
            f"{question}"
        )

    recall_at_5 = correct / len(questions)

    print("\n----------------------------")
    print(f"Correct: {correct}/{len(questions)}")
    print(f"Recall@5: {recall_at_5:.2%}")
    print("----------------------------")


if __name__ == "__main__":
    asyncio.run(evaluate_rag())
