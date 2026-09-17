from pathlib import Path

import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(path)
    pages = []

    for page in document:
        text = page.get_text()

        if text.strip():
            pages.append(text.strip())

    document.close()

    return "\n\n".join(pages)


def extract_pages_from_pdf(pdf_path: str) -> list[dict]:

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        # Extract text belonging only to this page.
        text = page.get_text().strip()

        # Ignore completely empty pages.
        if text:
            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    document.close()

    return pages