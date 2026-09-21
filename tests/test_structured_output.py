import pytest
from pydantic import ValidationError

from app.schemas import RAGResponse


def test_valid_rag_response():
    response = RAGResponse(
        answer="Redis is commonly used for caching.",
        sources=[
            {
                "document_id": 1,
                "metadata": {"topic": "redis"},
            }
        ],
        confidence=0.92,
    )

    assert response.answer.startswith("Redis")
    assert response.sources[0].document_id == 1
    assert response.confidence == 0.92


def test_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        RAGResponse(
            answer="Redis is used for caching.",
            sources=[],
            confidence=1.5,
        )