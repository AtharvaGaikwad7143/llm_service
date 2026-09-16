from app.ingestion.pdf_parser import extract_text_from_pdf


def main():
    # Read text from our sample PDF.
    text = extract_text_from_pdf("sample.pdf")

    print("\nExtracted text:\n")
    print(text)

    print("\nCharacter count:", len(text))


if __name__ == "__main__":
    main()