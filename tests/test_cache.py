import pytest

from app.services.cache import (
    build_rag_cache_key,
    get_cached_response,
    set_cached_response,
)


def test_cache_key_is_deterministic():
    key1 = build_rag_cache_key("What is Redis?")
    key2 = build_rag_cache_key("What is Redis?")

    assert key1 == key2


def test_cache_key_normalizes_question():
    key1 = build_rag_cache_key("What is Redis?")
    key2 = build_rag_cache_key("  WHAT IS REDIS?  ")

    assert key1 == key2


def test_different_questions_have_different_keys():
    key1 = build_rag_cache_key("What is Redis?")
    key2 = build_rag_cache_key("What is PostgreSQL?")

    assert key1 != key2


@pytest.mark.asyncio
async def test_cache_set_and_get():
    question = "cache integration test"
    response = {
        "question": question,
        "answer": "Redis is an in-memory data store.",
    }

    await set_cached_response(
        question,
        response,
        ttl=60,
    )

    cached = await get_cached_response(question)

    assert cached == response


@pytest.mark.asyncio
async def test_cache_miss():
    cached = await get_cached_response(
        "this question definitely does not exist in cache"
    )

    assert cached is None