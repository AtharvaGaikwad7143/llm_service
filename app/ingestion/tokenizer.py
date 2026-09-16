from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def count_tokens(text: str) -> int:

    tokens = tokenizer.encode(
        text,
        add_special_tokens=False,
        truncation=False,
    )

    return len(tokens)