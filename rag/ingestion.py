from rag.chunker import chunk_text
import os


def load_data(folder_path="Documents"):

    documents = []

    for file in os.listdir(folder_path):

        path = os.path.join(folder_path, file)

        if file.endswith(".txt"):

            with open(path, "r", encoding="utf-8") as f:
                documents.append(f.read())

    return "\n".join(documents)


# Testing
if __name__ == "__main__":

    with open("Documents/financial_knowledge_base.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    print(f"Total Chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk)