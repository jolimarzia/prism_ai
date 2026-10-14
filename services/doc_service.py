from pathlib import Path
from pypdf import PdfReader
from docx import Document
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from core.llm import embed


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if suffix == ".docx":
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file: {suffix}")


def chunk_text(text: str, size=800, overlap=100):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return [c for c in chunks if c.strip()]


def build_index(chunks):
    return np.array([embed(c) for c in chunks])


def retrieve(query, chunks, index, top_k=4):
    if not chunks:
        return []
    q = np.array([embed(query)])
    sims = cosine_similarity(q, index)[0]
    idx = sims.argsort()[::-1][:top_k]
    return [chunks[i] for i in idx]