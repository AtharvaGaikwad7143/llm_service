import pytest
from pydantic import ValidationError

from app.schemas import RAGResponse


def test_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        RAGResponse(
            answer="Redis is used for caching.",
            confidence=1.5,
        )


def test_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        RAGResponse(
            answer="Redis is used for caching.",
            sources=[],
            confidence=1.5,
        )