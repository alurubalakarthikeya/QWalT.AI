from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import faiss
import openai
from sentence_transformers import SentenceTransformer
from typing import List

# === Config ===
UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Simulated vector DB
doc_texts = []
doc_vectors = []

# === App Setup ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use specific origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic ===
class QueryRequest(BaseModel):
    message: str

# === Helper ===
def get_embedding(text: str):
    return EMBEDDING_MODEL.encode([text])[0]

def add_to_faiss(text: str):
    vector = get_embedding(text)
    doc_texts.append(text)
    doc_vectors.append(vector)

def search_similar(query: str, k=3):
    if not doc_vectors:
        return []

    query_vec = get_embedding(query).reshape(1, -1)
    index = faiss.IndexFlatL2(len(query_vec[0]))
    index.add(np.array(doc_vectors))
    D, I = index.search(query_vec, k)
    return [doc_texts[i] for i in I[0]]

def build_prompt(context: List[str], query: str):
    return (
        "Context:\n" + "\n---\n".join(context) +
        "\n\nQuestion: " + query + "\nAnswer:"
    )

def get_llm_response(prompt: str):
    import requests

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer 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",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# === Endpoints ===

@app.get("/")
def root():
    return {"message": "Bot Backend Running 🎉"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()  # Read once here
        buffer.write(content)
    text = content.decode("utf-8")
    add_to_faiss(text)

    return {"message": "File uploaded and indexed successfully."}


@app.post("/chat")
def chat_with_bot(payload: QueryRequest):
    query = payload.message
    similar_chunks = search_similar(query)
    prompt = build_prompt(similar_chunks, query)
    answer = get_llm_response(prompt)
    return {"response": answer}
