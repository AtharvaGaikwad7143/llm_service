from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()

def similarity(text_a: str, text_b: str) -> float:

    vector_a = np.array(embed_text(text_a))
    vector_b = np.array(embed_text(text_b))

    dot_product = np.dot(vector_a, vector_b)

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    score = dot_product / (norm_a * norm_b)

    return float(score)

def rank_documents(query : str, documents : list[str]) -> list[tuple[str, float]]:

    results = []

    for document in documents:
        score = similarity(query, document)
        results.append((document, score))

    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return results