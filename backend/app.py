from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from uuid import uuid4
from typing import List, Union
from contextlib import asynccontextmanager

import os
import json
import requests
import re

from utils.embed_store import embed_and_store, query_vector_store
from utils.extract_text import extract_text

load_dotenv()

# Model warm-up to reduce first response time
def warm_up_model():
    """Warm up the model with a simple request to reduce initial latency"""
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                },
                timeout=3
            )
    except:
        pass  # Ignore warm-up errors

# stores chat history as json 
HISTORY_DIR = "history_logs"
os.makedirs(HISTORY_DIR, exist_ok=True)

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

def analyze_query_completeness(query, chat_history, context_length=0):
    """
    Determines if we have enough information to provide a solution
    """
    query_lower = query.lower()
    word_count = len(query.split())

    # Specific problem indicators - can provide solution
    solution_indicators = [
        "error", "problem", "issue", "bug", "fix", "help", "how to", "what is",
        "explain", "process", "quality", "improve", "optimize", "lean", "six sigma",
        "defect", "variance", "control chart", "fishbone", "5 why", "kaizen",
        "efficiency", "productivity", "waste", "bottleneck", "workflow",
        "standard", "procedure", "training", "implementation", "analysis",
        "measurement", "kpi", "metric", "performance", "audit", "compliance"
    ]

    # Only require clarification for extremely vague queries
    extremely_vague = [
        "help me", "need help", "what do", "don't know", "confused",
        "something wrong", "not working", "having trouble"
    ]

    has_solution_context = any(term in query_lower for term in solution_indicators)
    is_extremely_vague = any(phrase in query_lower for phrase in extremely_vague) and word_count <= 4
    
    # If context available or has solution indicators, provide answer
    if context_length > 50 or has_solution_context:
        return True

    # Only ask for clarification if extremely vague and short
    if is_extremely_vague:
        return False

    # Default to providing helpful response for most queries
    return word_count >= 3

class QueryRequest(BaseModel):
    query: str
    file_name: str = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm up model in background
    import threading
    threading.Thread(target=warm_up_model, daemon=True).start()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(lifespan=lifespan)

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
    
@app.get("/")
def read_root():
    return {"message": "Backend is running"}

@app.post("/chat/")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id") or str(uuid4())
    query = data["query"]

    save_to_history(user_id, "user", query)
    chat_history = load_history(user_id)
    response = f"I received: '{query}' and have {len(chat_history)} messages in history."
    save_to_history(user_id, "bot", response)

    return {"response": response, "user_id": user_id}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    process_and_store(file_path, file.filename)
    print(f"Parsed filename list: {file.filename}")

    custom_prompt = f"You are an expert assistant for queries related to the document titled '{file.filename}'. Answer with clear and concise explanations based only on the given context."
    with open(os.path.join(PROMPT_DIR, f"{file.filename}.json"), "w") as f:
        json.dump({"system_prompt": custom_prompt}, f)

    # 👉 New: Generate initial suggested questions
    api_key = os.getenv("OPENROUTER_API_KEY")
    suggestion_prompt = (
        f"The user has just uploaded a file titled '{file.filename}'.\n"
        "Generate 3-4 short suggested questions (2–3 words) that could help explore the document.\n"
        "Examples: 'Summarize file', 'What's inside', 'Main points', 'Document scope'.\n"
        "Respond with a numbered list."
    )

    suggestions = []
    try:
        suggestion_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [{"role": "user", "content": suggestion_prompt}],
                "max_tokens": 30,
                "temperature": 0.6
            },
            timeout=5
        )

        if suggestion_response.status_code == 200:
            raw = suggestion_response.json()["choices"][0]["message"]["content"]
            for line in raw.strip().split('\n'):
                clean = re.sub(r'^\d+\.?\s*', '', line.strip())
                clean = clean.strip('."\'')
                if 1 < len(clean.split()) <= 3:
                    suggestions.append(clean)
            suggestions = suggestions[:4]
    except Exception as e:
        print(f">> Error generating upload suggestions: {e}")

    return {
        "message": f"{file.filename} uploaded, processed, and prompt saved.",
        "filename": file.filename,
        "suggested_questions": suggestions
    }


@app.post("/query")
async def query_document(
    query: str = Form(...),
    file_name: Union[List[str], str, None] = Form(None),
    user_id: str = Form(None)
):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    print(f">> Received query: '{query}' for files: '{file_name}'")

    if isinstance(file_name, str):
        file_name = [file_name]
    elif file_name is None:
        file_name = []

    context_parts = []
    high_quality_match = False

    for fname in file_name:
        try:
            result = query_vector_store(query, fname)
            if isinstance(result, dict):
                ctx = result.get("text", "")
                score = result.get("score", 0.0)
            else:
                ctx = str(result)
                score = 0.0

            if len(ctx) > 100 and score >= 0.6:
                high_quality_match = True

            context_parts.append(f"Document context for {fname}:\n{ctx}")
        except Exception as e:
            print(f">> Error querying vector store for {fname}: {e}")

    if context_parts:
        document_list = ", ".join(file_name)
        context = f"The following document(s) are relevant: {document_list}.\n\n" + "\n\n".join(context_parts)
    else:
        context = "No specific document context available."

    print(">>> Final context sent to LLM:\n", context)

    prompt_file = file_name[0] if file_name else None
    prompt_path = os.path.join(PROMPT_DIR, f"{prompt_file}.json") if prompt_file else None

    chat_history = load_history(user_id) if user_id else []

    conversation_context = ""
    if chat_history:
        recent_messages = chat_history[-6:]
        for message in recent_messages:
            role = "User" if message['role'] == 'user' else "Assistant"
            conversation_context += f"{role}: {message['message']}\n"

    has_enough_info = analyze_query_completeness(query, chat_history, context_length=len(context))
    if high_quality_match:
        has_enough_info = True

    if prompt_path and os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            base_system_prompt = json.load(f)["system_prompt"]
    else:
        base_system_prompt = (
            "You are QWalT, an expert quality improvement consultant with deep knowledge in: "
            "• Process optimization and Lean manufacturing • Six Sigma methodologies and DMAIC "
            "• Quality control tools (Fishbone, 5 Whys, Control Charts, Pareto Analysis) "
            "• Root cause analysis and problem-solving • KPI development and measurement "
            "• Workflow improvement and waste reduction • Standard operating procedures "
            "• Training and implementation strategies • Compliance and audit processes. "
            "Be conversational, practical, and solution-focused. Avoid formal structures or role tags."
        )

    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return {"error": "Missing API key."}

        if has_enough_info:
            system_prompt = (
                f"{base_system_prompt}\n\n"
                "Provide practical solutions. Be direct and concise. Use quality expertise."
            )
            user_prompt = f"""
{f'Context: {conversation_context[-150:]}' if conversation_context else ''}

Q: {query}

{f'Info: {context[:200]}' if context != 'No specific document context available.' else ''}

Answer:
"""
        else:
            system_prompt = (
                f"{base_system_prompt}\n\n"
                "Brief query. Give helpful guidance + ask ONE specific question."
            )
            user_prompt = f"""
{f'Context: {conversation_context[-100:]}' if conversation_context else ''}

Q: {query}

Give guidance + ask ONE question:
"""

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 180 if has_enough_info else 60,
            "temperature": 0.4
        }

        response_main = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )

        ai_reply = ""
        if response_main.status_code == 200:
            data = response_main.json()
            ai_reply = data["choices"][0]["message"]["content"].strip()

            if user_id:
                save_to_history(user_id, "user", query)
                save_to_history(user_id, "bot", ai_reply)
        else:
            return {"error": "Main AI request failed", "body": response_main.text}

        suggestion_prompt = f"Query: \"{query[:50]}\"\nGenerate 3 short questions (2-3 words). List format."


        suggestion_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "user", "content": suggestion_prompt}
                ],
                "max_tokens": 25,
                "temperature": 0.6
            },
            timeout=5
        )

        suggestions = []
        if suggestion_response.status_code == 200:
            raw = suggestion_response.json()["choices"][0]["message"]["content"]
            lines = raw.strip().split('\n')[:3]  # Limit to first 3 lines for speed
            for line in lines:
                clean_line = re.sub(r'^\d+\.?\s*', '', line.strip())
                clean_line = clean_line.strip('."\'')
                word_count = len(clean_line.split())
                if 1 < word_count <= 3:
                    suggestions.append(clean_line)
            suggestions = suggestions[:3]  # Maximum 3 suggestions

        return {
            "result": ai_reply,
            "needs_more_info": not has_enough_info,
            "follow_up_question": ai_reply if not has_enough_info else None,
            "suggested_questions": suggestions if suggestions else [],
            "analysis_mode": "solution" if has_enough_info else "clarification",
            "suggestions_note": "You can ask any of these next:"
        }



    except requests.RequestException as e:
        print(f">> Network error during AI call: {e}")
        return {"error": "Network error", "details": str(e)}
    except Exception as e:
        print(f">> Exception during AI call: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@app.post("/query-json")
async def query_document_json(request: QueryRequest):
    return await query_document(request.query, request.file_name)

@app.get("/health")
async def health_check():
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        return {
            "status": "healthy",
            "memory_mb": round(memory_mb, 2),
            "version": "optimized"
        }
    except ImportError:
        return {"status": "healthy", "version": "optimized"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")