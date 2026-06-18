from rag.Hybrid_retriver import hybrid_search
from rag.reranker import rerank_results
from rag.llm import generate_llm_response
from rag.risk_engine import calculate_risk_score, get_risk_level
from rag.query_classifier import classify_query

from rag.graph_store import load_graph
from rag.graphrag import graph_expand_query

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

    print(f"\n[Graph Expanded Query]: {expanded_query}")

    # HYBRID RETRIEVAL
    retrieved_chunks = hybrid_search(
        expanded_query
    )

    # RERANKING
    top_chunks = rerank_results(
        query,
        retrieved_chunks,
        top_k=3
    )

    # LLM RESPONSE
    final_response = generate_llm_response(
        query,
        top_chunks
    )

    # RISK SCORE
    risk_score = calculate_risk_score(
        " ".join(top_chunks)
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
        "evidence": top_chunks,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "category": category
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