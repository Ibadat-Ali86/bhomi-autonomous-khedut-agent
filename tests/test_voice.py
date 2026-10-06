import unittest
import wave
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bhomi.voice import transcribe_locally


def wav_bytes() -> bytes:
    stream = BytesIO()
    with wave.open(stream, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\0\0" * 1600)
    return stream.getvalue()


class VoiceTranscriptionTests(unittest.TestCase):
    def test_detected_speech_language_overrides_sidebar_fallback(self):
        model = Mock()
        model.transcribe.return_value = (
            iter([SimpleNamespace(text=" What is the weather? ")]),
            SimpleNamespace(language="en", language_probability=0.98),
        )
        with patch("bhomi.voice._load_model", return_value=model):
            result = transcribe_locally(wav_bytes(), "gu")
        self.assertEqual(result.state, "ready")
        self.assertEqual(result.text, "What is the weather?")
        self.assertEqual(result.language, "en")
        self.assertTrue(result.language_detected)
        self.assertIsNone(model.transcribe.call_args.kwargs["language"])

    def test_uncertain_language_uses_selected_language(self):
        model = Mock()
        model.transcribe.return_value = (
            iter([SimpleNamespace(text=" આજે હવામાન શું છે? ")]),
            SimpleNamespace(language="en", language_probability=0.31),
        )
        with patch("bhomi.voice._load_model", return_value=model):
            result = transcribe_locally(wav_bytes(), "gu")
        self.assertEqual(result.language, "gu")
        self.assertFalse(result.language_detected)

    def test_empty_and_invalid_audio_have_actionable_states(self):
        self.assertEqual(transcribe_locally(b"", "en").state, "empty_audio")
        self.assertEqual(transcribe_locally(wav_bytes(), "fr").state, "invalid_language")


if __name__ == "__main__":
    unittest.main()
