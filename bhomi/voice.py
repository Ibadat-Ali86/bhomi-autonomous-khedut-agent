"""Local speech recognition for the prototype's Gujarati/English voice input."""
from __future__ import annotations

import logging
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VoiceTranscript:
    text: str | None
    state: str
    language: str
    language_detected: bool


@st.cache_resource(show_spinner=False)
def _load_model(model_name: str):
    """Load Whisper once per app process instead of reloading on each message."""
    from faster_whisper import WhisperModel

    return WhisperModel(model_name, device="cpu", compute_type="int8")


def transcribe_locally(audio_bytes: bytes, language: str = "gu") -> VoiceTranscript:
    if os.getenv("BHOMI_LOCAL_ASR", "true").lower() not in {"1", "true", "yes", "on"}:
        return VoiceTranscript(None, "disabled", language if language in {"gu", "en"} else "gu", False)
    if not audio_bytes:
        return VoiceTranscript(None, "empty_audio", language if language in {"gu", "en"} else "gu", False)
    if len(audio_bytes) > 10 * 1024 * 1024:
        return VoiceTranscript(None, "audio_too_large", language if language in {"gu", "en"} else "gu", False)
    if language not in {"gu", "en"}:
        return VoiceTranscript(None, "invalid_language", "gu", False)
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        return VoiceTranscript(None, "missing_dependency", language, False)
    path = None
    stage = "audio_write"
    started = time.monotonic()
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
            audio_file.write(audio_bytes)
            path = Path(audio_file.name)
        stage = "model_load"
        model = _load_model(os.getenv("BHOMI_WHISPER_MODEL", "tiny"))
        stage = "transcribe"
        segments, info = model.transcribe(str(path), language=None, vad_filter=True)
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        detected_language = getattr(info, "language", None)
        detected_probability = getattr(info, "language_probability", 0.0) or 0.0
        use_detected = detected_language in {"gu", "en"} and detected_probability >= 0.5
        response_language = detected_language if use_detected else language
        if transcript:
            logger.info(
                "Voice transcription complete: stage=transcribe selected_language=%s response_language=%s detected=%s bytes=%d elapsed_ms=%d",
                language, response_language, use_detected,
                len(audio_bytes),
                round((time.monotonic() - started) * 1000),
            )
            return VoiceTranscript(transcript, "ready", response_language, use_detected)
        logger.info(
            "Voice transcription empty: stage=transcribe selected_language=%s response_language=%s detected=%s bytes=%d elapsed_ms=%d",
            language, response_language, use_detected,
            len(audio_bytes),
            round((time.monotonic() - started) * 1000),
        )
        return VoiceTranscript(None, "no_transcript", response_language, use_detected)
    except Exception as exc:
        logger.warning(
            "Voice transcription failed: stage=%s language=%s bytes=%d elapsed_ms=%d error_class=%s",
            stage,
            language,
            len(audio_bytes),
            round((time.monotonic() - started) * 1000),
            type(exc).__name__,
        )
        state = "model_unavailable" if stage == "model_load" else "transcription_failed"
        return VoiceTranscript(None, state, language, False)
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
