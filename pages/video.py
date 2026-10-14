import json
from pathlib import Path
import streamlit as st
from core.config import TEXT_MODEL
from core.llm import chat
from core.ui import hero
from core.storage import (
    load_history, add_history_entry, delete_history_entry, clear_history,
)


def _show_history():
    with st.sidebar:
        st.markdown("### 📚 Video History")
        entries = load_history("video")

        if not entries:
            st.caption("No history yet.")
            return

        if st.button("🗑️ Clear all", key="clear_video", use_container_width=True):
            clear_history("video")
            st.rerun()

        for entry in entries[:15]:
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            label = entry.get("title", "")[:35] or "Untitled"
            with st.expander(f"🎬 {label}\n_{ts}_"):
                st.caption(f"**Topic:** {entry.get('topic', '')}")
                st.caption(f"**Scenes:** {entry.get('num_scenes', 0)}")
                script = entry.get("script", [])
                if script:
                    st.caption("**Script preview:**")
                    for i, line in enumerate(script[:3], 1):
                        st.caption(f"{i}. {line}")
                fp = entry.get("file_path")
                if fp and Path(fp).exists():
                    st.download_button(
                        "⬇️ MP4",
                        Path(fp).read_bytes(),
                        file_name=Path(fp).name,
                        key=f"dl_video_{entry['id']}",
                    )
                if st.button("❌ Delete", key=f"del_video_{entry['id']}"):
                    delete_history_entry("video", entry["id"])
                    st.rerun()


def render():
    hero("Video Studio", "Turn a script into a slideshow video", icon="🎬")

    _show_history()

    st.markdown("### Create a video from a topic")

    col1, col2 = st.columns([3, 1])
    topic = col1.text_input("Topic", value="5 tips to stay productive", key="video_topic")
    n = col2.number_input("Scenes", min_value=3, max_value=10, value=5, key="video_scenes")

    sec = st.slider("Seconds per scene", min_value=2, max_value=8, value=3, key="video_sec_per_scene")

    col_a, col_b = st.columns(2)
    gen_script = col_a.button("1️⃣ Generate Script", use_container_width=True, key="btn_gen_script")
    make_video = col_b.button("2️⃣ Render Video", use_container_width=True, key="btn_make_video")

    if gen_script and topic:
        msgs = [
            {"role": "system", "content":
             "Return ONLY a JSON array of short on-screen text lines "
             "(max 12 words each). No markdown, no explanation. "
             'Example: ["Line 1", "Line 2", "Line 3"]'},
            {"role": "user", "content": f"Write {n} short lines for a video about: {topic}"},
        ]
        with st.spinner("Writing script…"):
            try:
                raw = chat(msgs, TEXT_MODEL, temperature=0.7)
                start = raw.find("[")
                end = raw.rfind("]") + 1
                lines = json.loads(raw[start:end])
                st.session_state.video_lines = lines
                st.success(f"✅ Script ready: {len(lines)} lines")
            except Exception:
                lines = [l.strip("-• *") for l in raw.splitlines() if l.strip()][:n]
                st.session_state.video_lines = lines
                st.warning("Used fallback parsing.")

    if "video_lines" in st.session_state:
        st.markdown("### 📝 Script")
        for i, line in enumerate(st.session_state.video_lines, 1):
            st.markdown(f"**{i}.** {line}")

    if make_video and "video_lines" in st.session_state:
        with st.spinner("Rendering video (may take 30-60s)…"):
            try:
                from services.video_service import build_video

                out_path = build_video(
                    st.session_state.video_lines,
                    out_name="prism_video.mp4",
                    seconds_per_line=sec,
                )
                st.success("✅ Video ready!")
                st.video(str(out_path))
                st.download_button("⬇️ Download MP4", out_path.read_bytes(),
                                   file_name="prism_video.mp4", mime="video/mp4")

                add_history_entry("video", {
                    "title": topic[:40],
                    "topic": topic,
                    "num_scenes": len(st.session_state.video_lines),
                    "script": st.session_state.video_lines,
                    "file_path": str(out_path),
                })
            except Exception as e:
                st.error(f"Video rendering failed: {e}")
                st.code(str(e))
    elif make_video:
        st.warning("⚠️ Please generate a script first.")