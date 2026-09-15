import asyncio

from sqlalchemy import text

from app.db.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            text("SELECT 1")
        )

        print("Database result:", result.scalar())


if __name__ == "__main__":
    asyncio.run(main())