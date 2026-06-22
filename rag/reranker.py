from sentence_transformers import CrossEncoder


# Load reranker model
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# CHANGED: now accepts the chroma similarity scores alongside the chunks,
# and returns a list of dicts (chunk, chroma_similarity, rerank_score)
# instead of bare chunk strings. Sort order/behavior is unchanged —
# we still rank by the cross-encoder's rerank score, just no longer
# throw the scores away afterward.
def rerank_results(query, retrieved_chunks, chroma_similarities, top_k=3):

    # Create query-chunk pairs
    pairs = []

    for chunk in retrieved_chunks:

        pairs.append([query, chunk])

    # Predict relevance scores
    raw_scores = reranker.predict(pairs)

    # Cross-encoder scores are unbounded logits; squash to 0-100 for display.
    # Ranking order is identical either way — this is presentation only.
    def to_pct(s):
        import math
        return round(100 / (1 + math.exp(-s)), 1)

    # Combine chunk + both scores
    scored_chunks = list(zip(
        retrieved_chunks,
        chroma_similarities,
        raw_scores
    ))

    # Sort by rerank score descending (unchanged behavior)
    scored_chunks.sort(
        key=lambda x: x[2],
        reverse=True
    )

    top_chunks = []

    for chunk, chroma_sim, rerank_score in scored_chunks[:top_k]:

        top_chunks.append({
            "text": chunk,
            "chroma_similarity": chroma_sim,
            "rerank_score": to_pct(rerank_score)
        })

    return top_chunks