from pathlib import Path

import pymupdf

def extract_text_from_pdf(pdf_path: str) -> str:

    path = Path(pdf_path)

    # Fail early if the requested PDF doesn't exist.
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Open the PDF document.
    document = pymupdf.open(path)

    pages = []

    # Extract text page by page.
    for page in document:
        text = page.get_text()

        # Store non-empty page text.
        if text.strip():
            pages.append(text.strip())

    # Close the PDF after extraction.
    document.close()

    # Combine all pages into one text document.
    return "\n\n".join(pages)