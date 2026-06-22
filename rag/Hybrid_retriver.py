from rag.chroma_store import search_chroma


def hybrid_search(query):

    print("\n[INFO] Searching ChromaDB...")

    # CHANGED: search_chroma now returns (documents, similarities) —
    # previously this only ever got documents, scores were unavailable
    # anywhere downstream.
    retrieved_chunks, similarities = search_chroma(
        query=query,
        top_k=3
    )

    print("\n[INFO] Retrieved Chunks:\n")

    for i, (chunk, sim) in enumerate(zip(retrieved_chunks, similarities), start=1):

        print(f"Chunk {i} [{sim}% match]:\n{chunk}\n")

    return retrieved_chunks, similarities


# Testing
if __name__ == "__main__":

    query = input("Enter your query: ")

    results, sims = hybrid_search(query)

    print("\nFinal Retrieved Results:\n")

    for r, s in zip(results, sims):

        print(f"[{s}%] {r}")
        print("-" * 50)