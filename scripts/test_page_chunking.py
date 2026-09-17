from app.ingestion.pdf_parser import extract_pages_from_pdf
from app.ingestion.chunker import chunk_pages
from app.ingestion.tokenizer import count_tokens


def main():
    # Extract the PDF while preserving page boundaries.
    pages = extract_pages_from_pdf("sample.pdf")

    # Chunk every page independently.
    chunks = chunk_pages(
        pages,
        chunk_size=500,
        overlap=50,
    )

    print("Total pages:", len(pages))
    print("Total chunks:", len(chunks))

    for chunk in chunks:
        print("\n" + "=" * 60)

        print(
            f"Page: {chunk['page_number']} | "
            f"Chunk: {chunk['chunk_index']}"
        )

        print(
            "Token count:",
            count_tokens(chunk["text"])
        )

        print("Text:")
        print(chunk["text"][:300])


if __name__ == "__main__":
    main()