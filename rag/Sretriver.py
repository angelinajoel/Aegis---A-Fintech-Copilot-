from chunker import chunk_text

# Load knowledge base
with open("documents/financial_knowledge_base.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = chunk_text(text)


def retrieve(query, top_k=3):
    query = query.lower()

    scored_chunks = []

    for chunk in chunks:
        chunk_lower = chunk.lower()

        # simple keyword match score
        score = 0

        for word in query.split():
            if word in chunk_lower:
                score += 1

        if score > 0:
            scored_chunks.append((score, chunk))

    # sort by best match
    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    return [chunk for score, chunk in scored_chunks[:top_k]]