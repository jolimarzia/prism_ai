
import json
import uuid
import base64
from datetime import datetime
from pathlib import Path

import streamlit as st
from openai import OpenAI

# ==================================================
# PRISM AI - LOCAL MULTIMODAL CHATBOT
# Powered by Ollama
# ==================================================

APP_NAME = "Prism AI"
TEXT_MODEL = "llama3.2:3b"
VISION_MODEL = "qwen2.5vl:3b"
OLLAMA_URL = "http://localhost:11434/v1"

HISTORY_FILE = Path(__file__).parent / "chat_history.json"
MAX_IMAGE_SIZE = 10 * 1024 * 1024

st.set_page_config(
    page_title="Prism AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- PREMIUM UI --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, #19264a 0%, transparent 48%),
        #080d18;
    color: #eef3ff;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: #0a1120;
    border-right: 1px solid #22314d;
}

h1, h2, h3 {
    color: #f3f6ff;
    letter-spacing: -0.5px;
}

[data-testid="stChatMessage"] {
    background: rgba(18, 29, 51, 0.82);
    border: 1px solid #22314d;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 12px;
}

[data-testid="stChatInput"] {
    border: 1px solid #5843a8;
    border-radius: 18px;
    background: #111b30;
    box-shadow: 0 0 24px rgba(112, 71, 255, 0.10);
}

.stButton > button {
    background: linear-gradient(115deg, #5937e8, #236fe9);
    color: white;
    border: 1px solid #7259ff;
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #7bdcff;
    box-shadow: 0 0 18px rgba(88, 111, 255, 0.3);
}

[data-testid="stFileUploader"] {
    background: rgba(16, 24, 42, 0.7);
    border: 1px dashed #4e5f91;
    border-radius: 16px;
    padding: 12px;
}

hr {
    border-color: #22314d;
}

.hero {
    padding: 26px 16px;
    text-align: center;
    border: 1px solid #26365a;
    border-radius: 24px;
    margin-bottom: 22px;
    background: linear-gradient(
        140deg,
        rgba(93, 65, 190, .18),
        rgba(23, 122, 215, .08),
        rgba(12, 20, 38, .55)
    );
}

.hero-title {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(90deg, #c7b6ff, #7a8cff, #50d9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.muted {
    color: #91a5c8;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero-title {
        font-size: 28px;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------- OLLAMA CLIENT --------------------

client = OpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    timeout=180.0,
)


# -------------------- HISTORY STORAGE --------------------

def load_chats():
    if not HISTORY_FILE.exists():
        return {}

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except (json.JSONDecodeError, OSError):
        st.warning(
            "Chat history পড়া যায়নি। "
            "chat_history.json ফাইলটি পরীক্ষা করো।"
        )
        return {}


def save_chats():
    temp_file = HISTORY_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(
            st.session_state.chats,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temp_file.replace(HISTORY_FILE)


def new_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "নতুন চ্যাট",
        "messages": [],
        "updated_at": datetime.now().isoformat(),
    }

    return chat_id


if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if not st.session_state.chats:
    chat_id = new_chat()
    st.session_state.selected_chat_id = chat_id
    save_chats()

if (
    "selected_chat_id" not in st.session_state
    or st.session_state.selected_chat_id
    not in st.session_state.chats
):
    st.session_state.selected_chat_id = next(
        iter(st.session_state.chats)
    )

if "upload_version" not in st.session_state:
    st.session_state.upload_version = 0


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown("# ✨ Prism AI")
    st.caption("Your local multimodal assistant")

    st.success("● Local AI mode")

    if st.button("＋ নতুন চ্যাট", use_container_width=True):
        chat_id = new_chat()
        st.session_state.selected_chat_id = chat_id
        save_chats()
        st.rerun()

    st.divider()
    st.subheader("📚 Chat History")

    chat_ids = sorted(
        st.session_state.chats.keys(),
        key=lambda cid: st.session_state.chats[cid].get(
            "updated_at", ""
        ),
        reverse=True,
    )

    for chat_id in chat_ids:
        title = st.session_state.chats[chat_id].get(
            "title", "নতুন চ্যাট"
        )
        is_selected = (
            chat_id == st.session_state.selected_chat_id
        )
        label = f"● {title}" if is_selected else title

        if st.button(
            label[:45],
            key=f"select_{chat_id}",
            use_container_width=True,
        ):
            st.session_state.selected_chat_id = chat_id
            st.rerun()

    st.divider()

    st.caption(f"Text model: {TEXT_MODEL}")
    st.caption(f"Vision model: {VISION_MODEL}")
    st.caption("History is stored on this computer.")

    if st.button("🗑️ এই চ্যাট মুছুন", use_container_width=True):
        selected_id = st.session_state.selected_chat_id
        st.session_state.chats.pop(selected_id, None)

        if not st.session_state.chats:
            selected_id = new_chat()
        else:
            selected_id = next(iter(st.session_state.chats))

        st.session_state.selected_chat_id = selected_id
        save_chats()
        st.rerun()


# -------------------- MAIN HEADER --------------------

st.markdown("""
<div class="hero">
    <div style="font-size:42px;">✦</div>
    <div class="hero-title">Welcome to Prism AI</div>
    <p class="muted">
        Your private, local AI assistant
    </p>
    <p class="muted">
        Chat naturally · Analyze images · Keep your history
    </p>
</div>
""", unsafe_allow_html=True)

current_chat = st.session_state.chats[
    st.session_state.selected_chat_id
]


# -------------------- DISPLAY CHAT --------------------

for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -------------------- IMAGE UPLOAD --------------------

st.markdown("#### 🖼️ ছবি আপলোড করো (ঐচ্ছিক)")

uploaded_image = st.file_uploader(
    "PNG, JPG, JPEG অথবা WEBP",
    type=["png", "jpg", "jpeg", "webp"],
    key=f"upload_{st.session_state.upload_version}",
    help="সর্বোচ্চ 10 MB। Vision model দিয়ে বিশ্লেষণ করা হবে।",
)

if uploaded_image and uploaded_image.size > MAX_IMAGE_SIZE:
    st.error("ছবির সাইজ 10 MB-এর কম হতে হবে।")
    uploaded_image = None

if uploaded_image:
    st.image(
        uploaded_image,
        caption="প্রশ্নের সঙ্গে এই ছবিটি পাঠানো হবে",
        width=320,
    )


# -------------------- MODEL RESPONSE --------------------

prompt = st.chat_input("Prism AI-কে কিছু জিজ্ঞেস করো...")

if prompt:
    # Select model according to whether an image is attached.
    model = VISION_MODEL if uploaded_image else TEXT_MODEL

    # Convert prior messages into model context.
    api_messages = [
        {
            "role": "system",
            "content": (
                "You are Prism AI, a helpful assistant. "
                "Reply in the same language as the user. "
                "Be accurate, clear, and friendly."
            ),
        }
    ]

    for old_message in current_chat["messages"]:
        api_messages.append({
            "role": old_message["role"],
            "content": old_message["content"],
        })

    # Build the current user message.
    if uploaded_image:
        image_base64 = base64.b64encode(
            uploaded_image.getvalue()
        ).decode("utf-8")

        mime_type = uploaded_image.type or "image/jpeg"

        user_content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        f"data:{mime_type};base64,{image_base64}"
                    )
                },
            },
        ]
    else:
        user_content = prompt

    api_messages.append({
        "role": "user",
        "content": user_content,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

        if uploaded_image:
            st.image(uploaded_image, width=280)

    with st.chat_message("assistant"):
        with st.spinner("Prism AI ভাবছে..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    temperature=0.7,
                )

                answer = (
                    response.choices[0].message.content
                    or "দুঃখিত, উত্তর পাওয়া যায়নি।"
                )

                st.markdown(answer)

                saved_prompt = prompt
                if uploaded_image:
                    saved_prompt += "\n\n[ছবি সংযুক্ত ছিল]"

                current_chat["messages"].append({
                    "role": "user",
                    "content": saved_prompt,
                })

                current_chat["messages"].append({
                    "role": "assistant",
                    "content": answer,
                })

                if current_chat["title"] == "নতুন চ্যাট":
                    title = prompt.strip() or "নতুন চ্যাট"
                    current_chat["title"] = title[:38]

                current_chat["updated_at"] = (
                    datetime.now().isoformat()
                )

                save_chats()

                if uploaded_image:
                    st.session_state.upload_version += 1

                st.rerun()

            except Exception as error:
                st.error("Ollama থেকে উত্তর পাওয়া যায়নি।")
                st.code(str(error))

                st.markdown("""
**যা পরীক্ষা করবে:**
1. Ollama চালু আছে কি না।
2. প্রয়োজনীয় মডেল ডাউনলোড হয়েছে কি না।
3. `http://localhost:11434` সার্ভার পাওয়া যাচ্ছে কি না।
""")

# -------------------- FOOTER --------------------

st.divider()
st.caption(
    "✨ Prism AI · Powered by Ollama · Local chat history"
)
