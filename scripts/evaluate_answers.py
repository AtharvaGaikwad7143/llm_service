import asyncio
import json
import os
import re

from app.services.rag_service import answer_question, hybrid_search
from app.services.reranker import rerank_documents
from app.services.llm import llm_service


QUESTIONS_FILE = "scripts/rag_eval_questions.json"
ANSWERS_FILE = "scripts/rag_eval_answers.json"


def normalize_text(text: str) -> set[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return set(words)


def token_overlap_score(
    generated_answer: str,
    reference_answer: str,
) -> float:
    generated_tokens = normalize_text(generated_answer)
    reference_tokens = normalize_text(reference_answer)

    if not reference_tokens:
        return 0.0

    overlap = generated_tokens & reference_tokens

    return len(overlap) / len(reference_tokens)


async def build_context(question: str) -> str:
    candidates = await hybrid_search(
        query=question,
        limit=20,
    )

    chunks = rerank_documents(
        query=question,
        documents=candidates,
        top_k=5,
    )

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Document {chunk['document_id']}]\n"
            f"{chunk['chunk_text']}"
        )

    return "\n\n".join(context_parts)


def load_saved_answers() -> dict:
    if not os.path.exists(ANSWERS_FILE):
        return {}

    with open(
        ANSWERS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_answers(data: dict) -> None:
    with open(
        ANSWERS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


async def generate_answers():
    with open(
        QUESTIONS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    saved_answers = load_saved_answers()

    for index, item in enumerate(
        questions,
        start=1,
    ):
        question = item["question"]

        if question in saved_answers:
            print(
                f"{index:02d}. CACHED | {question}"
            )
            continue

        try:
            result = await answer_question(question)

            saved_answers[question] = {
                "question": question,
                "reference_answer": item["reference_answer"],
                "generated_answer": result["answer"],
            }

            save_answers(saved_answers)

            print(
                f"{index:02d}. GENERATED | {question}"
            )

        except Exception as exc:
            print(
                f"{index:02d}. ERROR | "
                f"{question} | {exc}"
            )

    return saved_answers


async def evaluate_saved_answers():
    saved_answers = load_saved_answers()

    relevance_scores = []
    faithfulness_scores = []
    correctness_scores = []
    token_scores = []

    for index, item in enumerate(
        saved_answers.values(),
        start=1,
    ):
        question = item["question"]
        reference_answer = item["reference_answer"]
        generated_answer = item["generated_answer"]

        try:
            context = await build_context(question)

            token_score = token_overlap_score(
                generated_answer,
                reference_answer,
            )

            evaluation = (
                await llm_service.evaluate_rag_answer(
                    question=question,
                    context=context,
                    generated_answer=generated_answer,
                    reference_answer=reference_answer,
                )
            )

            token_scores.append(token_score)
            relevance_scores.append(
                evaluation.relevance
            )
            faithfulness_scores.append(
                evaluation.faithfulness
            )
            correctness_scores.append(
                evaluation.correctness
            )

            print(f"\n{index:02d}. {question}")
            print(
                f"Generated: {generated_answer}"
            )
            print(
                f"Token overlap: {token_score:.2%}"
            )
            print(
                f"Relevance: {evaluation.relevance:.2f}"
            )
            print(
                f"Faithfulness: "
                f"{evaluation.faithfulness:.2f}"
            )
            print(
                f"Correctness: "
                f"{evaluation.correctness:.2f}"
            )
            print(
                f"Reason: {evaluation.reason}"
            )

        except Exception as exc:
            print(
                f"\n{index:02d}. ERROR | "
                f"{question} | {exc}"
            )

    print("\n============================")
    print("RAG ANSWER EVALUATION")
    print("============================")

    if token_scores:
        print(
            f"Average token overlap: "
            f"{sum(token_scores) / len(token_scores):.2%}"
        )

        print(
            f"Average relevance: "
            f"{sum(relevance_scores) / len(relevance_scores):.2f}"
        )

        print(
            f"Average faithfulness: "
            f"{sum(faithfulness_scores) / len(faithfulness_scores):.2f}"
        )

        print(
            f"Average correctness: "
            f"{sum(correctness_scores) / len(correctness_scores):.2f}"
        )

        print(
            f"Evaluated questions: "
            f"{len(token_scores)}"
        )

    else:
        print("No questions were successfully evaluated.")

    print("============================")


async def main():
    print("\n============================")
    print("PHASE 1: GENERATE ANSWERS")
    print("============================")

    await generate_answers()

    print("\n============================")
    print("PHASE 2: LLM-AS-A-JUDGE")
    print("============================")

    await evaluate_saved_answers()


if __name__ == "__main__":
    asyncio.run(main())