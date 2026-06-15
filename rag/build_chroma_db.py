from rag.chunker import chunk_text
from rag.chroma_store import add_chunks_to_chroma

# Load knowledge base
with open("Documents/financial_knowledge_base.txt", "r", encoding="utf-8") as f:

    text = f.read()

# Chunking
chunks = chunk_text(text)

print(f"Total Chunks: {len(chunks)}")

# Store in Chroma
add_chunks_to_chroma(chunks)