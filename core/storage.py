import json
import uuid
from datetime import datetime
from pathlib import Path
from core.config import HISTORY_FILE, DATA_DIR

# All history files
HISTORY_DIR = DATA_DIR / "history"
HISTORY_DIR.mkdir(exist_ok=True)

FILES_DIR = DATA_DIR / "files"
FILES_DIR.mkdir(exist_ok=True)


# ============================================
# CHAT HISTORY (existing)
# ============================================
def load_chats():
    if not HISTORY_FILE.exists():
        return {}
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_chats(chats):
    tmp = HISTORY_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)
    tmp.replace(HISTORY_FILE)


def new_chat():
    cid = str(uuid.uuid4())
    return cid, {
        "title": "New chat",
        "messages": [],
        "updated_at": datetime.now().isoformat(),
    }


# ============================================
# GENERIC HISTORY (for Voice, Image, Slide, Video, Documents)
# ============================================
def _history_path(feature: str) -> Path:
    return HISTORY_DIR / f"{feature}_history.json"


def load_history(feature: str) -> list:
    path = _history_path(feature)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_history(feature: str, entries: list):
    path = _history_path(feature)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def add_history_entry(feature: str, entry: dict):
    entries = load_history(feature)
    entry["id"] = str(uuid.uuid4())
    entry["timestamp"] = datetime.now().isoformat()
    entries.insert(0, entry)
    save_history(feature, entries)
    return entry


def delete_history_entry(feature: str, entry_id: str):
    entries = load_history(feature)
    entries = [e for e in entries if e.get("id") != entry_id]
    save_history(feature, entries)


def clear_history(feature: str):
    save_history(feature, [])


# ============================================
# FILE SAVE HELPER
# ============================================
def save_generated_file(feature: str, filename: str, content: bytes) -> Path:
    feature_dir = FILES_DIR / feature
    feature_dir.mkdir(parents=True, exist_ok=True)
    out_path = feature_dir / filename
    with out_path.open("wb") as f:
        f.write(content)
    return out_path