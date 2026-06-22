from rag.Hybrid_retriver import hybrid_search
from rag.reranker import rerank_results
from rag.llm import generate_llm_response
from rag.risk_engine import calculate_risk_score, get_risk_level
from rag.query_classifier import classify_query

from rag.graph_store import load_graph
from rag.graphrag import graph_expand_query, get_traversed_subgraph

# -----------------------------------------
# LOAD GRAPH ONCE
# -----------------------------------------

graph = load_graph()


def generate_response(query):

    # GRAPH RAG EXPANSION
    expanded_query = graph_expand_query(
        graph,
        query
    )

    # NEW: capture the actual subgraph traversed (nodes + edges) so the
    # UI can draw it, instead of only having the flattened expanded
    # query string.
    subgraph = get_traversed_subgraph(
        graph,
        query
    )

    print(f"\n[Graph Expanded Query]: {expanded_query}")

    # HYBRID RETRIEVAL
    # CHANGED: now returns (chunks, chroma_similarities) instead of just chunks
    retrieved_chunks, chroma_similarities = hybrid_search(
        expanded_query
    )

    # RERANKING
    # CHANGED: now also receives chroma_similarities, and returns a list of
    # dicts carrying both scores instead of bare strings
    scored_chunks = rerank_results(
        query,
        retrieved_chunks,
        chroma_similarities,
        top_k=3
    )

    top_chunk_texts = [c["text"] for c in scored_chunks]

    # LLM RESPONSE
    final_response = generate_llm_response(
        query,
        top_chunk_texts
    )

    # RISK SCORE
    risk_score = calculate_risk_score(
        " ".join(top_chunk_texts)
    )

    risk_level = get_risk_level(
        risk_score
    )

    # QUERY CATEGORY
    category = classify_query(
        query
    )

    return {
        "answer": final_response,
        "evidence": top_chunk_texts,
        "scored_evidence": scored_chunks,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "category": category,
        "pipeline_trace": {
            "original_query": query,
            "expanded_query": expanded_query,
            "subgraph": subgraph,
        }
    }


if __name__ == "__main__":

    while True:

        query = input("\nAsk Aegis: ")

        if query.lower() == "exit":
            break

        result = generate_response(query)

        print("\n")
        print("=" * 60)
        print("Aegis AI Response")
        print("=" * 60)
        print(result["answer"])
        print("=" * 60)