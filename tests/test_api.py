import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_validation(client):
    response = client.post(
        "/generate",
        json={},
    )

    assert response.status_code == 422


def test_extract_validation(client):
    response = client.post(
        "/extract",
        json={},
    )

    assert response.status_code == 422


def test_query_validation(client):
    response = client.post(
        "/query",
        json={},
    )

    assert response.status_code == 422


def test_empty_question_rejected(client):
    response = client.post(
        "/query",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_empty_search_query_rejected(client):
    response = client.post(
        "/documents/search",
        json={
            "query": "",
            "limit": 5,
        },
    )

    assert response.status_code == 422


def test_search_limit_too_large(client):
    response = client.post(
        "/documents/search",
        json={
            "query": "Redis",
            "limit": 10000,
        },
    )

    assert response.status_code == 422