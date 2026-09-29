import hashlib
import json

from app.services.redis import redis_client


def build_rag_cache_key(question: str) -> str:
    normalized_question = " ".join(question.strip().lower().split())

    question_hash = hashlib.sha256(
        normalized_question.encode("utf-8")
    ).hexdigest()

    return f"rag:response:{question_hash}"


async def get_cached_response(question: str) -> dict | None:
    key = build_rag_cache_key(question)

    try:
        cached = await redis_client.get(key)

        if cached is None:
            return None

        return json.loads(cached)

    except Exception:
        return None


async def set_cached_response(
    question: str,
    response: dict,
    ttl: int,
) -> None:
    key = build_rag_cache_key(question)

    try:
        await redis_client.set(
            key,
            json.dumps(response),
            ex=ttl,
        )
    except Exception:
        pass