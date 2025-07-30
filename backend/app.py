from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from uuid import uuid4

import os
import json
import requests
from utils.embed_store import embed_and_store, query_vector_store
from utils.extract_text import extract_text
load_dotenv()
# stores chat history as json 
HISTORY_DIR = "history_logs"
os.makedirs(HISTORY_DIR, exist_ok=True)  # Ensure directory exists

def get_history_file(user_id):
    return os.path.join(HISTORY_DIR, f"{user_id}.json")

def load_history(user_id):
    filepath = get_history_file(user_id)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []

def save_to_history(user_id, role, message):
    filepath = get_history_file(user_id)
    history = load_history(user_id)
    history.append({"role": role, "message": message})
    with open(filepath, "w") as f:
        json.dump(history, f, indent=2)


# Pydantic model for JSON requests
class QueryRequest(BaseModel):
    query: str
    file_name: str = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "documents")
PROMPT_DIR = os.getenv("PROMPT_DIR", "prompts")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)

def process_and_store(file_path, file_name):
    text = extract_text(file_path)
    embed_and_store(text, file_name)

@app.post("/chat/")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id") or str(uuid4())  # If user_id not passed, generate new

    query = data["query"]

    # Save the user message
    save_to_history(user_id, "user", query)

    # Get the chat history (optional: pass to LLM for context)
    chat_history = load_history(user_id)

    # Your existing logic goes here (LLM or RAG with FAISS)
    # For now, fake response:
    response = f"I received: '{query}' and have {len(chat_history)} messages in history."

    # Save bot response
    save_to_history(user_id, "bot", response)

    return {"response": response, "user_id": user_id}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    process_and_store(file_path, file.filename)

    custom_prompt = f"You are an expert assistant for queries related to the document titled '{file.filename}'. Answer with clear and concise explanations based only on the given context."
    with open(os.path.join(PROMPT_DIR, f"{file.filename}.json"), "w") as f:
        json.dump({"system_prompt": custom_prompt}, f)

    return {"message": f"{file.filename} uploaded, processed, and prompt saved.", "filename": file.filename}

@app.post("/query")
async def query_document(query: str = Form(...), file_name: str = Form(None), user_id: str = Form(None)):
    # Validate inputs
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    print(f">> Received query: '{query}' for file: '{file_name}'")
    
    # If no file is specified, use a default context or handle gracefully
    if not file_name:
        print(">> No file specified, using default context")
        context = "No specific document context available."
    else:
        try:
            context = query_vector_store(query, file_name)
        except Exception as e:
            print(f">> Error querying vector store: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving context: {str(e)}")

    prompt_path = os.path.join(PROMPT_DIR, f"{file_name}.json") if file_name else None
    if prompt_path and os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            system_prompt = json.load(f)["system_prompt"]
    else:
        system_prompt = "You are a helpful assistant specializing in quality management and process improvement."

    user_prompt = f"""Use the following context to answer naturally and clearly.

Context:
{context}

Question:
{query}

Answer:"""

    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return {"error": "Missing API key."}

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
        )

        print(">> OpenRouter response code:", response.status_code)
        print(">> OpenRouter response body:", response.text) ##for reference guyssss

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                ai_reply = choices[0]["message"]["content"]
                if user_id:
                    save_to_history(user_id, "user", query)
                    save_to_history(user_id, "bot", ai_reply)
                return {"result": ai_reply}
            else:
                return {"error": "Empty or malformed response from model.", "raw": data}
        else:
            return {
                "error": "AI request failed",
                "status": response.status_code,
                "body": response.text
            }

    except Exception as e:
        print(f">> Exception during AI call: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@app.post("/query-json")
async def query_document_json(request: QueryRequest):
    """Alternative JSON endpoint for queries"""
    return await query_document(request.query, request.file_name)