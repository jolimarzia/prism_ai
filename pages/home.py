import streamlit as st
from core.ui import hero


def render():
    hero("Prism AI", "Your private, local multimodal AI studio", icon="✦")

    cols = st.columns(3)
    features = [
        ("💬", "Chat", "Talk with local LLM", "chat"),
        ("📄", "Documents", "Ask your PDFs & DOCX", "documents"),
        ("🎨", "Image Studio", "Text-to-image", "image"),
        ("📊", "Slide Studio", "Generate PPTX", "slide"),
    ]
    for i, (icon, name, desc, key) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <div style="font-size:34px;">{icon}</div>
                <h3 style="margin:6px 0;">{name}</h3>
                <p class="muted">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {name}", key=f"open_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()