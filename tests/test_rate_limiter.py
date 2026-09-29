import pytest
from fastapi import HTTPException

from app.services.rate_limiter import rate_limiter


class FakeRequest:
    def __init__(self, ip: str):
        self.client = type("Client", (), {"host": ip})()


class FakeRedis:
    def __init__(self):
        self.counts = {}
        self.ttl_value = 60
        self.expire_calls = []

    async def incr(self, key: str):
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int):
        self.expire_calls.append((key, seconds))

    async def ttl(self, key: str):
        return self.ttl_value


@pytest.mark.asyncio
async def test_rate_limiter_allows_first_five_requests(monkeypatch):
    fake_redis = FakeRedis()

    monkeypatch.setattr(
        "app.services.rate_limiter.redis_client",
        fake_redis,
    )

    request = FakeRequest("10.0.0.1")

    for _ in range(5):
        await rate_limiter(request)

    assert len(fake_redis.counts) == 1
    assert list(fake_redis.counts.values()) == [5]
    assert fake_redis.expire_calls[0][1] == 60


@pytest.mark.asyncio
async def test_rate_limiter_rejects_sixth_request(monkeypatch):
    fake_redis = FakeRedis()

    monkeypatch.setattr(
        "app.services.rate_limiter.redis_client",
        fake_redis,
    )

    request = FakeRequest("10.0.0.2")

    for _ in range(5):
        await rate_limiter(request)

    with pytest.raises(HTTPException) as exc_info:
        await rate_limiter(request)

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] == "60"


@pytest.mark.asyncio
async def test_different_ips_have_independent_limits(monkeypatch):
    fake_redis = FakeRedis()

    monkeypatch.setattr(
        "app.services.rate_limiter.redis_client",
        fake_redis,
    )

    request_a = FakeRequest("10.0.0.3")
    request_b = FakeRequest("10.0.0.4")

    for _ in range(5):
        await rate_limiter(request_a)

    for _ in range(5):
        await rate_limiter(request_b)

    assert len(fake_redis.counts) == 2
    assert all(count == 5 for count in fake_redis.counts.values())


@pytest.mark.asyncio
async def test_rate_limiter_fails_closed_when_redis_unavailable(monkeypatch):
    class BrokenRedis:
        async def incr(self, key: str):
            raise ConnectionError("Redis unavailable")

    monkeypatch.setattr(
        "app.services.rate_limiter.redis_client",
        BrokenRedis(),
    )

    request = FakeRequest("10.0.0.5")

    with pytest.raises(HTTPException) as exc_info:
        await rate_limiter(request)

    assert exc_info.value.status_code == 503