# config.py
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # dotenv not installed, will use system environment variables
    pass

# Paths
DATA_DIR = "data"
VECTOR_DIR = "vectorStore/faiss_index"
PROMPTS_DIR = "prompts"

# Retrieval
TOP_K = 4
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

# Embeddings / LLM - Using FREE alternatives
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Free local embeddings
LLM_MODEL = "gpt-4o-mini"  # Fallback to working model
USE_OPENAI = False  # Disable OpenAI to use free alternatives

# Env vars (disabled for free usage)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "disabled")
