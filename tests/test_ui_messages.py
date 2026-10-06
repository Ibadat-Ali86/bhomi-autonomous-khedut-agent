import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from bhomi.ui import answer_text_for_display


class MessageCompatibilityTests(unittest.TestCase):
    def test_legacy_user_message_without_language_fields_renders(self):
        message = {"role": "user", "text": "Hello"}
        self.assertEqual(answer_text_for_display(message, "en"), "Hello")

    def test_legacy_assistant_message_uses_text_fallback(self):
        message = {"role": "assistant", "text": "A prior response"}
        self.assertEqual(answer_text_for_display(message, "gu"), "A prior response")

    def test_groq_response_keeps_its_response_language(self):
        message = {
            "role": "assistant",
            "engine": "groq",
            "response_language": "gu",
            "text": "ગુજરાતી જવાબ",
            "text_en": "English fallback",
        }
        self.assertEqual(answer_text_for_display(message, "en"), "ગુજરાતી જવાબ")

    def test_local_voice_response_keeps_detected_language(self):
        message = {
            "role": "assistant",
            "engine": "local",
            "response_language": "en",
            "text": "English answer",
            "text_en": "English answer",
            "text_gu": "ગુજરાતી fallback",
        }
        self.assertEqual(answer_text_for_display(message, "gu"), "English answer")

    def test_chat_page_accepts_legacy_session_messages(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path))
        app.session_state["page"] = "chat"
        app.session_state["messages"] = [
            {"role": "user", "text": "Hello"},
            {"role": "assistant", "text": "Hello, farmer."},
        ]
        app.run()
        self.assertEqual(len(app.exception), 0)

    def test_typed_chat_uses_reviewed_fallback_in_both_languages(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        examples = [
            ("ગુજરાતી", "આવતીકાલનું હવામાન શું છે?", "નમૂના"),
            ("English", "What is tomorrow's weather?", "sample outlook"),
        ]
        for language, question, expected in examples:
            with self.subTest(language=language):
                app = AppTest.from_file(str(app_path))
                app.session_state["page"] = "chat"
                app.session_state["language"] = language
                app.run()
                app.chat_input[0].set_value(question).run()
                self.assertEqual(len(app.exception), 0)
                messages = app.session_state["messages"]
                self.assertEqual(len(messages), 2)
                self.assertEqual(messages[1]["engine_status"], "not_configured")
                self.assertIn(expected.lower(), messages[1]["text"].lower())

    def test_voice_answer_uses_detected_speech_language(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path))
        app.session_state["page"] = "chat"
        app.session_state["language"] = "ગુજરાતી"
        app.session_state["pending_voice"] = {
            "recording_id": "synthetic-test-recording",
            "audio_bytes": b"",
            "selected_language": "gu",
            "language": "en",
            "language_detected": True,
            "transcript": "What is tomorrow's weather?",
            "state": "ready",
            "revision": 0,
        }
        app.run()
        app.button(key="voice_send_confirmed").click().run()
        self.assertEqual(len(app.exception), 0)
        messages = app.session_state["messages"]
        self.assertEqual(messages[0]["language"], "en")
        self.assertEqual(messages[1]["response_language"], "en")
        self.assertIn("Light rain tomorrow", messages[1]["text"])

    def test_generated_reply_audio_uses_the_answer_language(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path))
        app.session_state["page"] = "chat"
        app.session_state["language"] = "ગુજરાતી"
        app.run()
        app.chat_input[0].set_value("આવતીકાલનું હવામાન શું છે?").run()
        with patch("bhomi.ui.synthesize_reply", return_value=b"fake-mp3") as synthesize:
            app.button(key="generate_speech-1").click().run()
        self.assertEqual(len(app.exception), 0)
        synthesize.assert_called_once()
        self.assertEqual(synthesize.call_args.args[1], "gu")


if __name__ == "__main__":
    unittest.main()
