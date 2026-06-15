from rag.chunker import chunk_text


# Load the knowledge base
with open("Documents/financial_knowledge_base.txt", "r", encoding="utf-8") as f:
    text = f.read()


# Convert text into chunks
chunks = chunk_text(text)


# Function to calculate score
def score_chunk(query, chunk):
    score = 0

    query_words = query.lower().split()
    chunk = chunk.lower()

    for word in query_words:
        if word in chunk:
            score += 1

    return score


# Main retrieval function
def retrieve(query, top_k=3):

    scored_chunks = []

    for chunk in chunks:

        score = score_chunk(query, chunk)

        if score > 0:
            scored_chunks.append((score, chunk))

    # Sort chunks by score (highest first)
    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    # Return top matching chunks
    results = [chunk for score, chunk in scored_chunks[:top_k]]

    return results


# Testing
if __name__ == "__main__":

    while True:

        query = input("\nAsk Aegis: ")

        results = retrieve(query)

        print("\n--- TOP MATCHES ---")

        if not results:
            print("No relevant information found.")

        for i, result in enumerate(results, start=1):
            print(f"\nResult {i}:")
            print(result)