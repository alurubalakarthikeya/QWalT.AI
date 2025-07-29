import faiss
import os
import numpy as np

INDEX_PATH = "vector_db/index.faiss"
TEXT_PATH = "vector_db/texts.npy"

def save_faiss_index(index, texts):
    faiss.write_index(index, INDEX_PATH)
    np.save(TEXT_PATH, texts)

def load_faiss_index():
    if not os.path.exists(INDEX_PATH):
        return None, []
    index = faiss.read_index(INDEX_PATH)
    texts = np.load(TEXT_PATH, allow_pickle=True)
    return index, texts

def search_index(index, query_vector, texts, top_k=5, query_text=None):
    D, I = index.search(query_vector, top_k)
    results = [texts[i] for i in I[0] if i < len(texts)]

    # Optional soft rerank by checking for keyword overlap
    if query_text:
        query_keywords = set(query_text.lower().split())
        def score(text):
            text_words = set(text.lower().split())
            overlap = query_keywords & text_words
            return len(overlap)
        results.sort(key=score, reverse=True)  # Higher overlap gets priority

    return results
