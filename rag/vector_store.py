import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Create FAISS index
def build_faiss_index(chunks):

    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))

    return index, embeddings


# Save index + chunks
def save_vector_db(index, chunks, path="vector_db"):

    faiss.write_index(index, f"{path}/faiss.index")

    with open(f"{path}/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Vector DB Saved")


# Load index + chunks
def load_vector_db(path="vector_db"):

    index = faiss.read_index(f"{path}/faiss.index")

    with open(f"{path}/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    print("✅ Vector DB Loaded")

    return index, chunks


# Search similar chunks
def search_similar_chunks(query, index, chunks, top_k=3):

    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    retrieved_chunks = []

    for idx in indices[0]:

        retrieved_chunks.append(chunks[idx])

    return retrieved_chunks