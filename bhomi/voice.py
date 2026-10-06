"""Local speech recognition for the prototype's Gujarati/English voice input."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st


@st.cache_resource(show_spinner=False)
def _load_model(model_name: str):
    """Load Whisper once per app process instead of reloading on each message."""
    from faster_whisper import WhisperModel

    return WhisperModel(model_name, device="cpu", compute_type="int8")

def transcribe_locally(audio_bytes: bytes, language: str = "gu") -> tuple[str | None, str]:
    if os.getenv("BHOMI_LOCAL_ASR", "true").lower() not in {"1", "true", "yes", "on"}:
        return None, "disabled"
    if not audio_bytes:
        return None, "empty_audio"
    if len(audio_bytes) > 10 * 1024 * 1024:
        return None, "audio_too_large"
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        return None, "missing_dependency"
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
            audio_file.write(audio_bytes)
            path = Path(audio_file.name)
        model = _load_model(os.getenv("BHOMI_WHISPER_MODEL", "tiny"))
        segments, _info = model.transcribe(str(path), language=language, vad_filter=True)
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        if transcript:
            return transcript, "ready"
        return None, "no_transcript"
    except Exception:
        return None, "transcription_failed"
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
