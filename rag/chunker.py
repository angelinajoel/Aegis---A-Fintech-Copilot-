import nltk

# Download tokenizer resources
nltk.download('punkt')
nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize


def chunk_text(text, chunk_size=5, overlap=1):

    # Split text into sentences
    sentences = sent_tokenize(text)

    chunks = []

    start = 0

    while start < len(sentences):

        end = start + chunk_size

        # Combine sentences into one chunk
        chunk = " ".join(sentences[start:end])

        chunks.append(chunk)

        # Move forward with overlap
        start += chunk_size - overlap

    return chunks


