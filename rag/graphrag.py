import networkx as nx
import spacy

from rag.domain_entities import ALL_DOMAIN_TERMS

nlp = spacy.load("en_core_web_sm")


def extract_domain_entities(text):
    """
    Finds occurrences of curated domain phrases (KYC, AML, structuring,
    risk score, etc.) in a chunk of text.

    WHY THIS EXISTS ALONGSIDE spaCy NER (not instead of it): spaCy's NER
    is trained to recognize real-world named entities — people, orgs,
    locations, dates. Compliance/policy prose is abstract domain
    language with very few of those, so NER alone returns close to
    nothing on this kind of text. Domain phrases ("anti-money
    laundering", "false positives", "structuring") are the actual
    recurring concepts this knowledge base's relationships are built
    around — they just aren't the *kind* of entity NER looks for.

    Matching strategy: simple case-insensitive substring matching against
    a curated, longest-phrase-first vocabulary (see domain_entities.py).
    This is intentionally simple rather than another ML model — for a
    fixed, curated vocabulary, substring matching is fast, fully
    deterministic, and easy to explain/debug, with no false negatives
    from a model misclassifying a known phrase.
    """

    text_lower = text.lower()
    found = []

    for term in ALL_DOMAIN_TERMS:
        if term in text_lower:
            found.append(term)

    return found


def build_graph(chunks):

    graph = nx.Graph()

    for chunk in chunks:

        doc = nlp(chunk)

        entities = []

        # Generic NER — kept as-is. If the knowledge base ever includes
        # real named entities (a specific bank, a named jurisdiction,
        # a dated regulation), these still get captured.
        for ent in doc.ents:
            entities.append(ent.text.lower())

        # NEW: domain-specific concept extraction — this is what
        # actually gives the graph something to work with on
        # compliance/policy text.
        entities.extend(extract_domain_entities(chunk))

        # De-duplicate while preserving order (a chunk could otherwise
        # list "kyc" twice if both NER and domain matching caught it)
        entities = list(dict.fromkeys(entities))

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

        if query in node or node in query:

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


def get_traversed_subgraph(graph, query):

    query = query.lower()

    matched_nodes = []
    edges = []

    for node in graph.nodes:

        # CHANGED: also match when the node is a substring of the query
        # (not just query-in-node). This matters because queries are
        # often phrased as full questions ("what is enhanced due
        # diligence") containing a domain phrase as a substring, while
        # nodes are the domain phrases themselves ("enhanced due
        # diligence") — the original one-directional check missed this
        # very common case.
        if query in node or node in query:

            matched_nodes.append(node)

            for neighbor in graph.neighbors(node):
                edges.append((node, neighbor))

    return {
        "matched_nodes": matched_nodes,
        "edges": edges
    }