from rag.chroma_store import search_chroma


def hybrid_search(query):

    print("\n[INFO] Searching ChromaDB...")

    retrieved_chunks = search_chroma(
        query=query,
        top_k=3
    )

    print("\n[INFO] Retrieved Chunks:\n")

    for i, chunk in enumerate(retrieved_chunks, start=1):

        print(f"Chunk {i}:\n{chunk}\n")

    return retrieved_chunks


# Testing
if __name__ == "__main__":

    query = input("Enter your query: ")

    results = hybrid_search(query)

    print("\nFinal Retrieved Results:\n")

    for r in results:

        print(r)
        print("-" * 50)