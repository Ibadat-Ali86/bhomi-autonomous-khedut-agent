"""Shared view helpers for cards, data provenance and Gujarati speech playback."""
import hashlib
import html

import streamlit as st
from bhomi.tts import SpeechGenerationError, synthesize_reply


def answer_text_for_display(answer: dict, language: str) -> str:
    """Choose message text while tolerating older session-state shapes."""
    response_language = answer.get("response_language")
    preferred_language = response_language if answer.get("role") == "assistant" and response_language in {"gu", "en"} else language
    for candidate in (answer.get(f"text_{preferred_language}"), answer.get("text"), answer.get("text_gu"), answer.get("text_en")):
        if isinstance(candidate, str) and candidate.strip():
            return candidate
    return ""


def card(title: str, value: str, detail: str, label: str = "નમૂના ડેટા", tone: str = "green") -> None:
    st.markdown(
        f'<section class="metric-card {tone}"><div class="card-top"><span>{html.escape(title)}</span>'
        f'<span class="pill">{html.escape(label)}</span></div><strong>{html.escape(value)}</strong>'
        f'<div class="card-detail">{html.escape(detail)}</div></section>',
        unsafe_allow_html=True,
    )


def speech_player(text: str, key: str, language: str = "gu") -> None:
    language = language if language in {"gu", "en"} else "gu"
    digest = hashlib.sha256(f"{language}\0{text}".encode("utf-8")).hexdigest()[:20]
    audio_cache = st.session_state.setdefault("reply_audio_cache", {})
    button_label = "Generate reply audio" if language == "en" else "જવાબનો અવાજ બનાવો"
    consent_note = (
        "When you generate audio, this reply text is sent to Microsoft's online speech service."
        if language == "en"
        else "અવાજ બનાવવા માટે આ જવાબનું લખાણ Microsoftની ઑનલાઇન સ્પીચ સેવા પાસે મોકલાશે."
    )
    with st.container(key=f"speech_{key}"):
        audio = audio_cache.get(digest)
        if audio is None:
            st.caption(consent_note)
            if st.button(button_label, key=f"generate_{key}", icon="🔊"):
                try:
                    with st.spinner("Generating Gujarati audio…" if language == "gu" else "Generating English audio…"):
                        audio = synthesize_reply(text, language)
                    audio_cache[digest] = audio
                    while len(audio_cache) > 5:
                        audio_cache.pop(next(iter(audio_cache)))
                except (SpeechGenerationError, ValueError):
                    st.warning(
                        "અવાજ બનાવી શકાયો નથી. ઇન્ટરનેટ જોડાણ તપાસીને ફરી પ્રયાસ કરો."
                        if language == "gu"
                        else "Could not generate audio. Check the internet connection and try again."
                    )
        if audio is not None:
            st.audio(audio, format="audio/mp3", autoplay=False, alt="Gujarati assistant reply" if language == "gu" else "English assistant reply")
