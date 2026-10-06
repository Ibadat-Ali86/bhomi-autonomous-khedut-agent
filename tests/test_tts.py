import unittest
from unittest.mock import AsyncMock, patch

from bhomi.tts import MAX_TEXT_LENGTH, SpeechGenerationError, synthesize_reply


class SpeechSynthesisTests(unittest.TestCase):
    def test_gujarati_reply_uses_gujarati_voice(self):
        with patch("bhomi.tts._generate_audio", new=AsyncMock(return_value=b"mp3")) as generate:
            result = synthesize_reply("  ગુજરાતી જવાબ  ", "gu")
        self.assertEqual(result, b"mp3")
        generate.assert_awaited_once_with("ગુજરાતી જવાબ", "gu-IN-DhwaniNeural")

    def test_english_reply_uses_indian_english_voice(self):
        with patch("bhomi.tts._generate_audio", new=AsyncMock(return_value=b"mp3")) as generate:
            synthesize_reply("English answer", "en")
        generate.assert_awaited_once_with("English answer", "en-IN-NeerjaNeural")

    def test_rejects_unsupported_language_and_oversized_reply(self):
        with self.assertRaises(ValueError):
            synthesize_reply("Hello", "fr")
        with self.assertRaises(SpeechGenerationError):
            synthesize_reply("x" * (MAX_TEXT_LENGTH + 1), "gu")


if __name__ == "__main__":
    unittest.main()
