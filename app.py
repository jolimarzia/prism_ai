
import streamlit as st

# Load secrets into environment variables (for Groq/cloud mode)
try:
    if "GROQ_API_KEY" in st.secrets:
        import os
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass  # secrets.toml not present, use .env or Ollama

st.set_page_config(
    page_title="Prism AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.ui import inject_css
inject_css()

# --- Pages ---
PAGES = {
    "home":      ("🏠", "Home"),
    "chat":      ("💬", "Chat"),
    "documents": ("📄", "Documents"),
    "voice":     ("🎙️", "Voice Studio"),
    "image":     ("🎨", "Image Studio"),
    "slide":     ("📊", "Slide Studio"),
    "video":     ("🎬", "Video Studio"),
}

if "page" not in st.session_state:
    st.session_state.page = "home"

with st.sidebar:
    st.markdown("# ✨ Prism AI")
    st.caption("Local multimodal AI studio")
    st.divider()
    for key, (icon, label) in PAGES.items():
        selected = st.session_state.page == key
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            st.session_state.page = key
            st.rerun()
    st.divider()
    st.caption("Powered by Ollama · Local-first")

# --- Router ---
page = st.session_state.page

if page == "home":
    from pages.home import render
elif page == "chat":
    from pages.chat import render
elif page == "documents":
    from pages.documents import render
elif page == "voice":
    from pages.voice import render
elif page == "image":
    from pages.image import render
elif page == "slide":
    from pages.slide import render
elif page == "video":
    from pages.video import render
else:
    st.error("Unknown page")
    st.stop()

render()