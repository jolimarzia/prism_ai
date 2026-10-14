from pathlib import Path
import streamlit as st
from services.image_service import expand_prompt, generate_image
from core.ui import hero
from core.storage import (
    load_history, add_history_entry, delete_history_entry, clear_history,
    save_generated_file,
)


def _show_history():
    with st.sidebar:
        st.markdown("### 📚 Image History")
        entries = load_history("image")

        if not entries:
            st.caption("No history yet.")
            return

        if st.button("🗑️ Clear all", key="clear_image", use_container_width=True):
            clear_history("image")
            st.rerun()

        for entry in entries[:15]:
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            label = entry.get("title", "")[:35] or "Untitled"
            with st.expander(f"🎨 {label}\n_{ts}_"):
                st.caption(f"**Prompt:** {entry.get('prompt', '')[:150]}")
                if entry.get("enhanced_prompt"):
                    st.caption(f"**Enhanced:** {entry['enhanced_prompt'][:150]}")
                fp = entry.get("file_path")
                if fp and Path(fp).exists():
                    st.image(fp, width=200)
                    st.download_button(
                        "⬇️ PNG",
                        Path(fp).read_bytes(),
                        file_name=Path(fp).name,
                        key=f"dl_img_{entry['id']}",
                    )
                if st.button("❌ Delete", key=f"del_img_{entry['id']}"):
                    delete_history_entry("image", entry["id"])
                    st.rerun()


def render():
    hero("Image Studio", "Turn ideas into images", icon="🎨")

    _show_history()

    prompt = st.text_area("Describe your image", height=120)
    col1, col2 = st.columns(2)
    w = col1.slider("Width", 256, 1024, 768, 64)
    h = col2.slider("Height", 256, 1024, 768, 64)

    if prompt and st.button("✨ Generate", use_container_width=True):
        with st.spinner("Expanding prompt…"):
            enhanced = expand_prompt(prompt)
        st.caption(f"**Enhanced prompt:** {enhanced}")

        with st.spinner("Rendering image…"):
            try:
                data = generate_image(enhanced, w, h)
                st.image(data, use_column_width=True)
                st.download_button("⬇️ Download PNG", data,
                                   file_name="prism_image.png")

                # Save to history
                fname = f"img_{len(load_history('image')) + 1}.png"
                saved_path = save_generated_file("image", fname, data)

                add_history_entry("image", {
                    "title": prompt[:40],
                    "prompt": prompt,
                    "enhanced_prompt": enhanced,
                    "width": w,
                    "height": h,
                    "file_path": str(saved_path),
                })

            except Exception as e:
                st.error(f"Generation failed: {e}")