from rag.chunker import chunk_text

with open("documents/financial_knowledge_base.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = chunk_text(text)

print(f"Total Chunks: {len(chunks)}")

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk)