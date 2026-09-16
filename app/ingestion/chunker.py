from app.ingestion.tokenizer import tokenizer


def chunk_text_by_tokens(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    # Convert the entire document into token IDs.
    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
        truncation=False,
    )

    chunks = []

    # Move forward by chunk_size - overlap.
    step = chunk_size - overlap

    for start in range(0, len(token_ids), step):
        end = start + chunk_size

        # Select this chunk's token IDs.
        chunk_token_ids = token_ids[start:end]

        if not chunk_token_ids:
            break

        # Convert token IDs back into readable text.
        chunk = tokenizer.decode(
            chunk_token_ids,
            skip_special_tokens=True,
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(token_ids):
            break

    return chunks