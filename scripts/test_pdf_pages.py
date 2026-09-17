from app.ingestion.pdf_parser import extract_pages_from_pdf


def main():
    pages = extract_pages_from_pdf("sample.pdf")

    print("Total non-empty pages:", len(pages))

    for page in pages:
        print("\n" + "=" * 60)
        print(f"PAGE {page['page_number']}")
        print("=" * 60)

        print("Characters:", len(page["text"]))
        print("Preview:")
        print(page["text"][:300])


if __name__ == "__main__":
    main()