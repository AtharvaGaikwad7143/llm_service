from app.ingestion.pdf_parser import extract_text_from_pdf
from app.ingestion.chunker import chunk_text_by_tokens
from app.ingestion.tokenizer import count_tokens


def main():
    # Extract text from the PDF.
    text = extract_text_from_pdf("sample.pdf")

    print("Original characters:", len(text))
    print("Original tokens:", count_tokens(text))

    # Compare the three chunk sizes required by the roadmap.
    for chunk_size in [300, 500, 800]:
        chunks = chunk_text_by_tokens(
            text,
            chunk_size=chunk_size,
            overlap=50,
        )

        print("\n" + "=" * 60)
        print(f"CHUNK SIZE: {chunk_size} TOKENS")
        print("=" * 60)

        print("Number of chunks:", len(chunks))

        for index, chunk in enumerate(chunks[:3], start=1):
            print(f"\n--- Chunk {index} ---")
            print("Token count:", count_tokens(chunk))
            print("Preview:", chunk[:300])


if __name__ == "__main__":
    main()