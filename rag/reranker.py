from sentence_transformers import CrossEncoder


# Load reranker model
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_results(query, retrieved_chunks, top_k=3):

    # Create query-chunk pairs
    pairs = []

    for chunk in retrieved_chunks:

        pairs.append([query, chunk])

    # Predict relevance scores
    scores = reranker.predict(pairs)

    # Combine chunks with scores
    scored_chunks = list(zip(retrieved_chunks, scores))

    # Sort by score descending
    scored_chunks.sort(
        key=lambda x: x[1],
        reverse=True
    )

    # Return top chunks
    top_chunks = []

    for chunk, score in scored_chunks[:top_k]:

        top_chunks.append(chunk)

    return top_chunks