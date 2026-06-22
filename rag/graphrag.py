import networkx as nx
import spacy

nlp = spacy.load("en_core_web_sm")


def build_graph(chunks):

    graph = nx.Graph()

    for chunk in chunks:

        doc = nlp(chunk)

        entities = []

        for ent in doc.ents:
            entities.append(ent.text.lower())

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):

                entity1 = entities[i]
                entity2 = entities[j]

                graph.add_edge(entity1, entity2)

    return graph


def get_related_entities(graph, query):

    query = query.lower()

    related = set()

    for node in graph.nodes:

        if query in node:

            neighbors = list(graph.neighbors(node))

            for n in neighbors:
                related.add(n)

    return list(related)


def graph_expand_query(graph, query):

    related_entities = get_related_entities(
        graph,
        query
    )

    expanded_query = query + " " + " ".join(related_entities)

    return expanded_query


# NEW: same matching logic as get_related_entities, but returns the
# actual (matched_node, neighbor) edge pairs instead of a flat set of
# neighbor names. This is what lets the UI draw the real traversed
# subgraph instead of just listing words.
def get_traversed_subgraph(graph, query):

    query = query.lower()

    matched_nodes = []
    edges = []

    for node in graph.nodes:

        if query in node:

            matched_nodes.append(node)

            for neighbor in graph.neighbors(node):
                edges.append((node, neighbor))

    return {
        "matched_nodes": matched_nodes,
        "edges": edges
    }