import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Prism AI"
TEXT_MODEL = os.getenv(
    "TEXT_MODEL",
    "openai/gpt-oss-120b"
)
VISION_MODEL = os.getenv("VISION_MODEL", "qwen2.5vl:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = ROOT / "chat_history.json"
MAX_IMAGE_SIZE = 10 * 1024 * 1024