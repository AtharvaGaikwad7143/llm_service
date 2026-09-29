import time

from fastapi import HTTPException, Request, status

from app.services.redis import redis_client


RATE_LIMIT = 5
WINDOW_SECONDS = 60


async def rate_limiter(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"

    current_window = int(time.time()) // WINDOW_SECONDS

    key = f"rate_limit:{client_ip}:{current_window}"

    try:
        count = await redis_client.incr(key)

        if count == 1:
            await redis_client.expire(key, WINDOW_SECONDS)

        if count > RATE_LIMIT:
            ttl = await redis_client.ttl(key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
                headers={
                    "Retry-After": str(max(ttl, 0)),
                },
            )

    except HTTPException:
        raise

    except Exception:
        # Rate limiter failure → fail closed.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiting service unavailable.",
        )