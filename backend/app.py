from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
import json

from utils.processor import process_and_store, query_vector_store

load_dotenv()

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
async def query_document(query: str = Form(...), file_name: str = Form(...)):
    context = query_vector_store(query, file_name)

    prompt_path = os.path.join(PROMPT_DIR, f"{file_name}.json")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            system_prompt = json.load(f)["system_prompt"]
    else:
        system_prompt = "You are a helpful assistant."

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
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
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
        print(">> OpenRouter response body:", response.text)

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                ai_reply = choices[0]["message"]["content"]
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
        return {"error": "Exception during AI call", "message": str(e)}
