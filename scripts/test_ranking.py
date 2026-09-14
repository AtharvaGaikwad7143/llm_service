from app.services.embeddings import rank_documents

query = "What is Redis used for?"

documents = [
    "Redis is an in-memory data store.",
    "PostgreSQL is a relational database.",
    "Redis can be used for caching.",
    "The Eiffel Tower is located in Paris.",
    "Redis supports fast key-value operations.",
]

results = rank_documents(
    query=query,
    documents=documents,
)

for document, score in results:
    print(f"{score:.4f} -> {document}")