from pathlib import Path
from core.config import DATA_DIR

# Lazy loading — only load when needed
_whisper_model = None


def _get_whisper_model():
    """Lazy-load Whisper model. Uses 'tiny' for fast deployment."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _whisper_model


def transcribe(audio_path: Path) -> str:
    """Convert audio to text."""
    model = _get_whisper_model()
    segments, info = model.transcribe(str(audio_path), beam_size=5)
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip()


def synthesize(text: str, out_name: str = "tts.mp3", lang: str = "en") -> Path:
    """Convert text to speech using gTTS."""
    from gtts import gTTS
    out_path = DATA_DIR / out_name
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(str(out_path))
    return out_path