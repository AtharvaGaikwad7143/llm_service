import asyncio

from app.repositories.document_repository import (
    create_document,
    get_document,
)


async def main():
    # Create a test document in PostgreSQL.
    document_id = await create_document(
        filename="test.txt",
        content="This is a test document.",
    )

    print("Created document:", document_id)

    # Read the document back using its generated ID.
    document = await get_document(document_id)

    print("\nRetrieved document:")
    print(document)


if __name__ == "__main__":
    asyncio.run(main())