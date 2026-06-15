import networkx as nx
import spacy

nlp = spacy.load("en_core_web_sm")

graph = nx.Graph()


def build_graph(chunks):

    for chunk in chunks:

        doc = nlp(chunk)

        entities = []

        for ent in doc.ents:
            entities.append(ent.text)

        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):

                entity1 = entities[i]
                entity2 = entities[j]

                graph.add_edge(entity1, entity2)

    return graph


def get_related_entities(entity):

    if entity in graph:
        return list(graph.neighbors(entity))

    return []


import matplotlib.pyplot as plt


def visualize_graph():

    plt.figure(figsize=(12, 8))

    nx.draw(
        graph,
        with_labels=True,
        node_size=2000,
        font_size=10
    )

    plt.show()