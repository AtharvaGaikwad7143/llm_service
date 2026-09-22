import asyncio
import json

from app.services.rag_service import hybrid_search


QUESTIONS_FILE = "scripts/rag_eval_questions.json"


async def evaluate_rag():
    # Load the evaluation dataset.
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    correct = 0
    reciprocal_rank_sum = 0.0

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        expected_document_id = item["expected_document_id"]

        # Run hybrid retrieval.
        results = await hybrid_search(
            query=question,
            limit=5,
        )

        retrieved_document_ids = [
            result["document_id"]
            for result in results
        ]

        # Recall@5:
        # Did the expected document appear anywhere in top 5?
        is_correct = (
            expected_document_id in retrieved_document_ids
        )

        if is_correct:
            correct += 1

        # MRR@5:
        # Find the rank of the first relevant result.
        if expected_document_id in retrieved_document_ids:
            rank = retrieved_document_ids.index(
                expected_document_id
            ) + 1

            reciprocal_rank_sum += 1 / rank

        status = "PASS" if is_correct else "FAIL"

        print(
            f"{index:02d}. {status} | "
            f"Expected: {expected_document_id} | "
            f"Retrieved: {retrieved_document_ids} | "
            f"{question}"
        )

    recall_at_5 = correct / len(questions)
    mrr_at_5 = reciprocal_rank_sum / len(questions)

    print("\n----------------------------")
    print(f"Correct: {correct}/{len(questions)}")
    print(f"Recall@5: {recall_at_5:.2%}")
    print(f"MRR@5:    {mrr_at_5:.4f}")
    print("----------------------------")


if __name__ == "__main__":
    asyncio.run(evaluate_rag())