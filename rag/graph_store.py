import pickle


def save_graph(graph, path="graph.pkl"):

    with open(path, "wb") as f:
        pickle.dump(graph, f)


def load_graph(path="graph.pkl"):

    with open(path, "rb") as f:
        return pickle.load(f)