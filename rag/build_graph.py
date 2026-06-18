from rag.chunker import chunk_text
from rag.ingestion import load_data

from rag.graphrag import build_graph
from rag.graph_store import save_graph


# LOAD DATA
documents = load_data()

# CREATE CHUNKS
chunks = chunk_text(documents)

# BUILD GRAPH
graph = build_graph(chunks)

# SAVE GRAPH
save_graph(graph)

print("Graph built successfully!")