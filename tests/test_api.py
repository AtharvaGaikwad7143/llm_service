from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_validation():
    response = client.post(
        "/generate",
        json={}
    )

    assert response.status_code == 422


def test_extract_validation():
    response = client.post(
        "/extract",
        json={}
    )

    assert response.status_code == 422