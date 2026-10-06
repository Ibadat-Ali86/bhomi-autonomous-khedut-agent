"""On-demand speech generation for English and Gujarati assistant replies."""

import asyncio
from io import BytesIO

VOICES = {
    "gu": "gu-IN-DhwaniNeural",
    "en": "en-IN-NeerjaNeural",
}
MAX_TEXT_LENGTH = 3000
MAX_AUDIO_BYTES = 5 * 1024 * 1024
TIMEOUT_SECONDS = 30


class SpeechGenerationError(RuntimeError):
    """Raised when the online speech service cannot produce playable audio."""


async def _generate_audio(text: str, voice: str) -> bytes:
    import edge_tts

    communicator = edge_tts.Communicate(text, voice)
    audio = BytesIO()
    async with asyncio.timeout(TIMEOUT_SECONDS):
        async for chunk in communicator.stream():
            if chunk.get("type") == "audio":
                audio.write(chunk["data"])
                if audio.tell() > MAX_AUDIO_BYTES:
                    raise SpeechGenerationError("Generated audio is too large.")
    result = audio.getvalue()
    if not result:
        raise SpeechGenerationError("The speech service returned no audio.")
    return result


def synthesize_reply(text: str, language: str) -> bytes:
    """Return MP3 audio for a reply using the voice matching its language."""
    if language not in VOICES:
        raise ValueError("Unsupported speech language.")
    normalized_text = text.strip()
    if not normalized_text:
        raise ValueError("Speech text cannot be empty.")
    if len(normalized_text) > MAX_TEXT_LENGTH:
        raise SpeechGenerationError("Reply is too long to generate speech.")

    try:
        return asyncio.run(_generate_audio(normalized_text, VOICES[language]))
    except SpeechGenerationError:
        raise
    except Exception as exc:
        # Do not include request text or provider response details in logs/UI.
        raise SpeechGenerationError("Online speech generation failed.") from exc
