
import os
import streamlit as st
from openai import OpenAI
from core.config import OLLAMA_URL, EMBED_MODEL

# DUAL PROVIDER: Ollama (local) OR Groq (cloud)

GROQ_API_KEY = str(
    st.secrets.get("GROQ_API_KEY", "")
    or os.getenv("GROQ_API_KEY", "")
).strip()

if GROQ_API_KEY:
    # Cloud mode: Groq
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
        timeout=120.0,
    )
    TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
    # Groq has no reliable vision model on free tier
    # Fall back to local Ollama for vision if available
    VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "openai/gpt-oss-20b")
    MODE = "groq"
else:
    # Local mode: Ollama
    client = OpenAI(
        base_url=OLLAMA_URL,
        api_key="ollama",
        timeout=300.0,
    )
    from core.config import TEXT_MODEL as OLLAMA_TEXT
    from core.config import VISION_MODEL as OLLAMA_VISION
    TEXT_MODEL = OLLAMA_TEXT
    VISION_MODEL = OLLAMA_VISION
    MODE = "ollama"


SYSTEM_PROMPT = (
    "You are Prism AI, a helpful, accurate, friendly multimodal assistant. "
    "You can see and analyze images when they are attached. "
    "Reply in the same language the user writes in."
)


def chat(messages, model=None, temperature=0.7):
    """Chat completion. Uses TEXT_MODEL if model is None."""
    if model is None:
        model = TEXT_MODEL
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def embed(text: str):
    """Embeddings — only available in Ollama mode."""
    if MODE != "ollama":
        raise RuntimeError(
            "Embeddings require Ollama. Set up Ollama locally for Documents feature."
        )
    resp = client.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding