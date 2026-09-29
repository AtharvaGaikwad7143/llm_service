from fastapi.testclient import TestClient

from app.main import app


class FakeRedis:
    def __init__(self):
        self.counts = {}
        self.ttl_value = 60

    async def incr(self, key: str):
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int):
        pass

    async def ttl(self, key: str):
        return self.ttl_value


def test_query_rate_limit(monkeypatch):
    fake_redis = FakeRedis()

    monkeypatch.setattr(
        "app.services.rate_limiter.redis_client",
        fake_redis,
    )

    async def fake_answer_question(question: str):
        return {
            "answer": "test answer",
            "confidence": 1.0,
        }

    monkeypatch.setattr(
        "app.api.routes.query.answer_question",
        fake_answer_question,
    )

    client = TestClient(app)

    responses = []

    for _ in range(6):
        responses.append(
            client.post(
                "/query",
                json={"question": "test rate limiting"},
            )
        )

    assert [response.status_code for response in responses[:5]] == [
        200, 200, 200, 200, 200
    ]

    assert responses[5].status_code == 429
    assert responses[5].headers["Retry-After"] == "60"