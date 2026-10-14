import tempfile
from pathlib import Path
import streamlit as st
from core.config import TEXT_MODEL
from core.llm import chat, SYSTEM_PROMPT
from services.doc_service import extract_text, chunk_text, build_index, retrieve
from core.ui import hero
from core.storage import (
    load_history, add_history_entry, delete_history_entry, clear_history,
)


def _show_history():
    with st.sidebar:
        st.markdown("### 📚 Document History")
        entries = load_history("documents")

        if not entries:
            st.caption("No history yet.")
            return

        if st.button("🗑️ Clear all", key="clear_docs", use_container_width=True):
            clear_history("documents")
            st.rerun()

        for entry in entries[:15]:
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            label = entry.get("title", "")[:35] or "Untitled"
            with st.expander(f"{label}\n_{ts}_"):
                st.caption(f"**Question:** {entry.get('question', '')[:200]}")
                st.caption(f"**Answer:** {entry.get('answer', '')[:200]}")
                if st.button("❌ Delete", key=f"del_doc_{entry['id']}"):
                    delete_history_entry("documents", entry["id"])
                    st.rerun()


def render():
    hero("Documents", "Ask questions about your PDFs, DOCX, TXT", icon="📄")

    _show_history()

    uploaded = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )

    if uploaded and st.button("📚 Index documents", use_container_width=True):
        with st.spinner("Parsing & embedding…"):
            chunks = []
            for f in uploaded:
                suffix = Path(f.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(f.getvalue())
                    tmp_path = Path(tmp.name)
                try:
                    text = extract_text(tmp_path)
                    chunks.extend(chunk_text(text))
                finally:
                    tmp_path.unlink(missing_ok=True)

            st.session_state.doc_chunks = chunks
            st.session_state.doc_index = build_index(chunks) if chunks else None
            st.session_state.doc_names = [f.name for f in uploaded]
            st.success(f"Indexed {len(chunks)} chunks from {len(uploaded)} file(s).")

    if "doc_chunks" not in st.session_state:
        st.info("Upload & index documents to begin.")
        return

    q = st.text_input("Your question")
    if q and st.button("Ask", use_container_width=True):
        ctx_chunks = retrieve(q, st.session_state.doc_chunks, st.session_state.doc_index)
        context = "\n\n---\n\n".join(ctx_chunks)
        msgs = [
            {"role": "system", "content": SYSTEM_PROMPT +
             "\nAnswer ONLY from the provided context. If unknown, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"},
        ]
        with st.spinner("Thinking…"):
            answer = chat(msgs, TEXT_MODEL, temperature=0.3)
            st.markdown(answer)

            add_history_entry("documents", {
                "title": q[:40],
                "question": q,
                "answer": answer,
                "documents": st.session_state.get("doc_names", []),
            })