import chromadb
from sentence_transformers import SentenceTransformer

# Persistent Chroma client
client = chromadb.PersistentClient(path="chroma_db")

# Create collection
collection = client.get_or_create_collection(
    name="financial_risk_db"
)

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Add chunks to DB
def add_chunks_to_chroma(chunks):

    embeddings = model.encode(chunks).tolist()

    ids = [f"id_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

    print("✅ Chunks added to ChromaDB")


# Search similar chunks
# CHANGED: Chroma already computes a distance for every match — we were
# throwing it away. Now we return it too, so the UI can show a real
# similarity score per chunk instead of nothing.
def search_chroma(query, top_k=3):

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    documents = results["documents"][0]
    distances = results["distances"][0]

    # Chroma's default distance is squared L2 (lower = more similar).
    # Convert to an intuitive 0-100 "similarity %" for display purposes only.
    # This is a presentation transform, not a new metric — the underlying
    # ranking is unchanged.
    similarities = [
        round(max(0, (1 - d)) * 100, 1)
        for d in distances
    ]

    return documents, similarities


# Testing
if __name__ == "__main__":

    query = input("Enter your query: ")

    docs, sims = search_chroma(query)

    print("\nFinal Retrieved Results:\n")

    for doc, sim in zip(docs, sims):
        print(f"[{sim}%] {doc}")
        print("-" * 50)