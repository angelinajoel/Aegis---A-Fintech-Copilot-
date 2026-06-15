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
def search_chroma(query, top_k=3):

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results["documents"][0]