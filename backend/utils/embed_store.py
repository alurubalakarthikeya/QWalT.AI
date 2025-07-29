from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_DIR = "vector_db"
if not os.path.exists(VECTOR_DIR):
    os.makedirs(VECTOR_DIR)

def embed_and_store(text, file_name):
    import re
    import textwrap

    # Split text using heading-like patterns
    section_pattern = r"(?:\n|^)(\d[\d\.]*[\)\.]?|Step \d+|Section \d+)[^\n]*\n"
    sections = re.split(section_pattern, text)

    structured_chunks = []
    i = 0
    while i < len(sections):
        if re.match(section_pattern, sections[i]):
            heading = sections[i].strip()
            if i + 1 < len(sections):
                content = sections[i + 1].strip()
                full_text = f"{heading}: {content}"
                # Wrap cleanly into ~450-character chunks without breaking words
                chunks = textwrap.wrap(full_text, width=450, break_long_words=False, break_on_hyphens=False)
                structured_chunks.extend(chunks)
                i += 2
            else:
                i += 1
        else:
            plain = sections[i].strip()
            chunks = textwrap.wrap(plain, width=450, break_long_words=False, break_on_hyphens=False)
            structured_chunks.extend(chunks)
            i += 1

    embeddings = model.encode(structured_chunks)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    # Save index
    faiss.write_index(index, os.path.join(VECTOR_DIR, f"{file_name}.index"))

    # Save chunks for retrieval
    with open(os.path.join(VECTOR_DIR, f"{file_name}_chunks.pkl"), "wb") as f:
        pickle.dump(structured_chunks, f)



def query_vector_store(query, file_name, top_k=3):
    # Load index and chunks
    index_path = os.path.join(VECTOR_DIR, f"{file_name}.index")
    chunks_path = os.path.join(VECTOR_DIR, f"{file_name}_chunks.pkl")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        return "Document not indexed."

    index = faiss.read_index(index_path)

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), top_k)

    results = [chunks[i] for i in indices[0]]
    return "\n\n".join(results)
