from rag.chunker import chunk_text
from rag.vector_store import (
    build_faiss_index,
    save_vector_db
)

# Load knowledge base
with open("Documents/financial_knowledge_base.txt", "r", encoding="utf-8") as f:

    text = f.read()

# Create chunks
chunks = chunk_text(text)

print(f"Total Chunks: {len(chunks)}")

# Build index
index, embeddings = build_faiss_index(chunks)

# Save DB
save_vector_db(index, chunks)