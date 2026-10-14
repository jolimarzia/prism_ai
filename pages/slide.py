import json
from pathlib import Path
import streamlit as st
from core.config import TEXT_MODEL
from core.llm import chat
from services.slide_service import build_pptx
from core.ui import hero
from core.storage import (
    load_history, add_history_entry, delete_history_entry, clear_history,
)


def _show_history():
    with st.sidebar:
        st.markdown("### 📚 Slide History")
        entries = load_history("slide")

        if not entries:
            st.caption("No history yet.")
            return

        if st.button("🗑️ Clear all", key="clear_slide", use_container_width=True):
            clear_history("slide")
            st.rerun()

        for entry in entries[:15]:
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            label = entry.get("title", "")[:35] or "Untitled"
            with st.expander(f"📊 {label}\n_{ts}_"):
                st.caption(f"**Topic:** {entry.get('topic', '')}")
                st.caption(f"**Slides:** {entry.get('num_slides', 0)}")
                fp = entry.get("file_path")
                if fp and Path(fp).exists():
                    st.download_button(
                        "⬇️ PPTX",
                        Path(fp).read_bytes(),
                        file_name=Path(fp).name,
                        key=f"dl_slide_{entry['id']}",
                    )
                if st.button("❌ Delete", key=f"del_slide_{entry['id']}"):
                    delete_history_entry("slide", entry["id"])
                    st.rerun()


def render():
    hero("Slide Studio", "Generate PowerPoint from a topic", icon="📊")

    _show_history()

    topic = st.text_input("Topic", "The future of renewable energy")
    n = st.slider("Number of slides", 3, 15, 6)

    if topic and st.button("📊 Generate slides", use_container_width=True):
        msgs = [
            {"role": "system", "content":
             'Return ONLY valid JSON: {"slides":[{"title":"..",'
             '"bullets":["..",".."]}]}. No markdown, no explanation.'},
            {"role": "user", "content": f"Create {n} slides about: {topic}"},
        ]
        with st.spinner("Designing slides…"):
            raw = chat(msgs, TEXT_MODEL, temperature=0.6)

        try:
            data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        except Exception:
            st.error("Model returned invalid JSON. Try again.")
            st.code(raw)
            return

        for i, s in enumerate(data["slides"], 1):
            st.markdown(f"### {i}. {s.get('title', '')}")
            for b in s.get("bullets", []):
                st.markdown(f"- {b}")

        path = build_pptx(topic, data["slides"])
        st.download_button("⬇️ Download PPTX", path.read_bytes(),
                           file_name="prism_slides.pptx")

        add_history_entry("slide", {
            "title": topic[:40],
            "topic": topic,
            "num_slides": len(data["slides"]),
            "file_path": str(path),
        })