import tempfile
from pathlib import Path
import streamlit as st
from core.ui import hero
from core.storage import (
    load_history, add_history_entry, delete_history_entry, clear_history,
)


def _show_history():
    with st.sidebar:
        st.markdown("### 📚 Voice History")
        entries = load_history("voice")

        if not entries:
            st.caption("No history yet.")
            return

        if st.button("🗑️ Clear all", key="clear_voice", use_container_width=True):
            clear_history("voice")
            st.rerun()

        for entry in entries[:15]:
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            label = entry.get("title", "")[:35] or "Untitled"
            etype = entry.get("type", "")
            icon = "🎧" if etype == "transcribe" else "🔊"
            with st.expander(f"{icon} {label}\n_{ts}_"):
                if etype == "transcribe":
                    st.caption(f"**File:** {entry.get('source_file', '')}")
                    st.caption(f"**Transcript:** {entry.get('transcript', '')[:200]}")
                else:
                    st.caption(f"**Language:** {entry.get('language', '')}")
                    st.caption(f"**Text:** {entry.get('text', '')[:200]}")
                    fp = entry.get("file_path")
                    if fp and Path(fp).exists():
                        st.audio(fp)
                        st.download_button(
                            "⬇️ MP3",
                            Path(fp).read_bytes(),
                            file_name=Path(fp).name,
                            key=f"dl_voice_{entry['id']}",
                        )
                if st.button("❌ Delete", key=f"del_voice_{entry['id']}"):
                    delete_history_entry("voice", entry["id"])
                    st.rerun()


def render():
    hero("Voice Studio", "Speech-to-text and Text-to-speech", icon="🎙️")

    _show_history()

    tab1, tab2 = st.tabs(["🎧 Transcribe (audio → text)", "🔊 Speak (text → audio)"])

    # ============ TAB 1: Transcription ============
    with tab1:
        st.markdown("### Upload audio and convert to text")
        audio = st.file_uploader(
            "Upload audio (wav, mp3, m4a, ogg)",
            type=["wav", "mp3", "m4a", "ogg"],
            key="voice_transcribe_upload",
        )

        if audio:
            st.audio(audio)

            if st.button("🎧 Transcribe", use_container_width=True, key="btn_transcribe"):
                with st.spinner("Loading Whisper model (first run may take a minute)…"):
                    try:
                        from services.voice_service import transcribe

                        suffix = Path(audio.name).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(audio.getvalue())
                            tmp_path = Path(tmp.name)

                        with st.spinner("Transcribing…"):
                            text = transcribe(tmp_path)

                        tmp_path.unlink(missing_ok=True)

                        st.success("✅ Transcription complete!")
                        st.text_area("Transcript", text, height=220, key="transcript_output")

                        add_history_entry("voice", {
                            "title": audio.name,
                            "type": "transcribe",
                            "source_file": audio.name,
                            "transcript": text,
                        })

                    except Exception as e:
                        st.error(f"Transcription failed: {e}")
                        st.code(str(e))

    # ============ TAB 2: Text-to-speech ============
    with tab2:
        st.markdown("### Enter text and generate audio")
        text = st.text_area(
            "Text to speak",
            height=180,
            key="voice_tts_text",
            placeholder="Type or paste text here…",
        )

        col1, col2 = st.columns([1, 3])
        lang = col1.selectbox(
            "Language",
            ["en", "bn", "hi", "ar", "es", "fr", "de", "ja", "zh-CN"],
            key="voice_tts_lang",
        )
        col2.markdown("")

        if st.button("🔊 Generate Audio", use_container_width=True, key="btn_tts"):
            if not text.strip():
                st.warning("Please enter some text first.")
            else:
                with st.spinner("Synthesizing audio…"):
                    try:
                        from services.voice_service import synthesize

                        fname = f"tts_{len(load_history('voice')) + 1}.mp3"
                        out_path = synthesize(text, out_name=fname, lang=lang)
                        st.success("✅ Audio generated!")

                        st.audio(str(out_path))
                        st.download_button(
                            "⬇️ Download MP3",
                            out_path.read_bytes(),
                            file_name=fname,
                            mime="audio/mpeg",
                            key="dl_tts",
                        )

                        add_history_entry("voice", {
                            "title": text[:40],
                            "type": "tts",
                            "language": lang,
                            "text": text,
                            "file_path": str(out_path),
                        })

                    except Exception as e:
                        st.error(f"TTS failed: {e}")
                        st.code(str(e))