import base64
from datetime import datetime
import streamlit as st
from core.config import MAX_IMAGE_SIZE
from core.llm import TEXT_MODEL, VISION_MODEL
from core.llm import chat, SYSTEM_PROMPT
from core.storage import load_chats, save_chats, new_chat
from core.ui import hero


def _init_state():
    if "chats" not in st.session_state:
        st.session_state.chats = load_chats()
    if not st.session_state.chats:
        cid, obj = new_chat()
        st.session_state.chats[cid] = obj
        st.session_state.selected_chat_id = cid
        save_chats(st.session_state.chats)
    if ("selected_chat_id" not in st.session_state
            or st.session_state.selected_chat_id not in st.session_state.chats):
        st.session_state.selected_chat_id = next(iter(st.session_state.chats))
    if "upload_version" not in st.session_state:
        st.session_state.upload_version = 0


def _sidebar():
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        if st.button("＋ New chat", use_container_width=True):
            cid, obj = new_chat()
            st.session_state.chats[cid] = obj
            st.session_state.selected_chat_id = cid
            save_chats(st.session_state.chats)
            st.rerun()

        st.divider()
        ids = sorted(
            st.session_state.chats.keys(),
            key=lambda c: st.session_state.chats[c].get("updated_at", ""),
            reverse=True,
        )
        for cid in ids:
            title = st.session_state.chats[cid].get("title", "New chat")
            sel = cid == st.session_state.selected_chat_id
            if st.button(("● " if sel else "") + title[:42],
                         key=f"sel_{cid}", use_container_width=True):
                st.session_state.selected_chat_id = cid
                st.rerun()

        st.divider()
        if st.button("🗑️ Delete this chat", use_container_width=True):
            st.session_state.chats.pop(st.session_state.selected_chat_id, None)
            if not st.session_state.chats:
                cid, obj = new_chat()
                st.session_state.chats[cid] = obj
                st.session_state.selected_chat_id = cid
            else:
                st.session_state.selected_chat_id = next(iter(st.session_state.chats))
            save_chats(st.session_state.chats)
            st.rerun()


def render():
    _init_state()
    _sidebar()

    hero("Chat", "Local text + vision conversation", icon="💬")
    current = st.session_state.chats[st.session_state.selected_chat_id]

    for m in current["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    uploaded = st.file_uploader(
        "🖼️ Attach image (optional)",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"up_{st.session_state.upload_version}",
    )
    if uploaded and uploaded.size > MAX_IMAGE_SIZE:
        st.error("Image must be < 10 MB")
        uploaded = None
    if uploaded:
        st.image(uploaded, width=300)

    prompt = st.chat_input("Ask Prism AI…")
    if not prompt:
        return

    model = VISION_MODEL if uploaded else TEXT_MODEL
    api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for old in current["messages"]:
        api_msgs.append({"role": old["role"], "content": old["content"]})

    if uploaded:
        b64 = base64.b64encode(uploaded.getvalue()).decode()
        mime = uploaded.type or "image/jpeg"
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        ]
    else:
        user_content = prompt

    api_msgs.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded:
            st.image(uploaded, width=280)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                answer = chat(api_msgs, model)
                st.markdown(answer)
                saved = prompt + ("\n\n[image attached]" if uploaded else "")
                current["messages"].append({"role": "user", "content": saved})
                current["messages"].append({"role": "assistant", "content": answer})
                if current["title"] == "New chat":
                    current["title"] = (prompt.strip() or "New chat")[:38]
                current["updated_at"] = datetime.now().isoformat()
                save_chats(st.session_state.chats)
                if uploaded:
                    st.session_state.upload_version += 1
                st.rerun()
            except Exception as e:
                st.error("Ollama error")
                st.code(str(e))