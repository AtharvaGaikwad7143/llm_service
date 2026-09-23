import pytest

from app.ingestion.chunker import (
    chunk_text_by_tokens,
    chunk_pages,
)


def test_empty_text():
    result = chunk_text_by_tokens("")

    assert result == []


def test_short_text():
    text = "Redis is an in-memory data store."

    result = chunk_text_by_tokens(text)

    assert len(result) == 1
    assert "redis" in result[0].lower()


def test_chunk_size_validation():
    with pytest.raises(
        ValueError,
        match="chunk_size must be greater than 0",
    ):
        chunk_text_by_tokens(
            "Redis is fast.",
            chunk_size=0,
        )


def test_negative_overlap_validation():
    with pytest.raises(
        ValueError,
        match="overlap cannot be negative",
    ):
        chunk_text_by_tokens(
            "Redis is fast.",
            overlap=-1,
        )


def test_overlap_validation():
    with pytest.raises(
        ValueError,
        match="overlap must be smaller than chunk_size",
    ):
        chunk_text_by_tokens(
            "Redis is fast.",
            chunk_size=100,
            overlap=100,
        )


def test_chunks_are_created():
    text = " ".join(
        ["Redis is an in-memory data store."] * 100
    )

    result = chunk_text_by_tokens(
        text,
        chunk_size=50,
        overlap=10,
    )

    assert len(result) > 1


def test_chunk_pages_preserves_page_number():
    pages = [
        {
            "page_number": 1,
            "text": "Redis is an in-memory data store.",
        },
        {
            "page_number": 2,
            "text": "PostgreSQL stores structured data.",
        },
    ]

    result = chunk_pages(
        pages,
        chunk_size=50,
        overlap=10,
    )

    assert len(result) == 2
    assert result[0]["page_number"] == 1
    assert result[1]["page_number"] == 2


def test_chunk_pages_contains_required_metadata():
    pages = [
        {
            "page_number": 3,
            "text": "Docker packages applications into containers.",
        }
    ]

    result = chunk_pages(
        pages,
        chunk_size=50,
        overlap=10,
    )

    assert len(result) == 1

    chunk = result[0]

    assert "page_number" in chunk
    assert "chunk_index" in chunk
    assert "text" in chunk