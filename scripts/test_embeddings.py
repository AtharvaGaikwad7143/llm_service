from app.services.embeddings import embed_text

text = "Redis is an in-memory data store."

embedding = embed_text(text)

print("Dimensions: ", len(embedding))

print("Printing first 5 values: ", embedding[:5])