from rag.Hybrid_retriver import hybrid_search
from rag.reranker import rerank_results
from rag.llm import generate_llm_response
from rag.graphrag import build_graph, get_related_entities


def generate_response(query):

    # -----------------------------------
    # STEP 1: HYBRID RETRIEVAL
    # -----------------------------------

    retrieved_chunks = hybrid_search(query)

    # -----------------------------------
    # STEP 2: RERANKING
    # -----------------------------------

    top_chunks = rerank_results(
        query,
        retrieved_chunks,
        top_k=3
    )

    # -----------------------------------
    # STEP 3: BUILD KNOWLEDGE GRAPH
    # -----------------------------------

    build_graph(top_chunks)

    # -----------------------------------
    # STEP 4: FIND RELATED ENTITIES
    # -----------------------------------

    related_entities = get_related_entities(query)

    # -----------------------------------
    # STEP 5: PREPARE EXTRA CONTEXT
    # -----------------------------------

    graph_context = ""

    if related_entities:
        graph_context = (
            "Related Risk Entities:\n"
            + ", ".join(related_entities)
        )

    # -----------------------------------
    # STEP 6: LLM GENERATION
    # -----------------------------------

    final_response = generate_llm_response(
        query,
        top_chunks + [graph_context]
    )

    return final_response


# -----------------------------------
# MAIN LOOP
# -----------------------------------

if __name__ == "__main__":

    while True:

        query = input("\nAsk Aegis: ")

        if query.lower() == "exit":
            break

        answer = generate_response(query)

        print("\n")
        print("=" * 60)
        print("Aegis AI Response")
        print("=" * 60)
        print(answer)
        print("=" * 60)