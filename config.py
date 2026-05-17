import os
from dotenv import load_dotenv

load_dotenv()

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")

# Hugging Face fallback settings
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "google/gemma-4-31B-it")

# Runtime switch: set USE_OLLAMA=false on HF Spaces, true locally
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

# Whisper STT settings
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "hi")  # covers Marathi + Hindi

# Image constraints
MAX_IMAGE_DIMENSION = 1024  # pixels; Gemma 4 E4B handles up to this efficiently

# Gradio server settings
GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
GRADIO_SHARE = os.getenv("GRADIO_SHARE", "false").lower() == "true"
