from app.services.embeddings import similarity

# When identical
text_a = "Redis is an in-memory data store."
text_b = "Redis is an in-memory data store."

score = similarity(text_a, text_b)

print("Identical:")
print("Score:", score)

# When related
text_a = "Redis is an in-memory data store."
text_b = "Redis stores data in memory."

score = similarity(text_a, text_b)

print("\nRelated:")
print("Score:", score)

# When unrelated
text_a = "Redis is an in-memory data store."
text_b = "The weather is beautiful today."

score = similarity(text_a, text_b)

print("\nUnrelated:")
print("Score:", score)

