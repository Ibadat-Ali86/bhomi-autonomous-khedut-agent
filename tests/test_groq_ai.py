import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bhomi.demo_data import load_demo_data
from bhomi.groq_ai import generate_groq_reply


class GroqAssistantTests(unittest.TestCase):
    def setUp(self):
        data = load_demo_data()
        self.farm = data["farms"]["fields"][0]
        self.weather = data["weather"][0]
        self.price = data["prices"][0]
        self.alert = data["alerts"][0]
        self.advisory = data["advisories"][0]

    def generate(self, question="What should I check today?", language="en", intent="unsupported", history=None):
        return generate_groq_reply(
            question=question,
            language=language,
            intent=intent,
            farm=self.farm,
            weather=self.weather,
            price=self.price,
            alert=self.alert,
            advisory=self.advisory,
            fallback_text="Reviewed demo reply",
            history=history or [],
        )

    def test_missing_key_uses_not_configured_status_without_network(self):
        with patch("bhomi.groq_ai.get_groq_api_key", return_value=""):
            reply = self.generate()
        self.assertEqual(reply.status, "not_configured")
        self.assertIsNone(reply.text)

    def test_high_risk_questions_never_call_groq(self):
        with patch("bhomi.groq_ai.get_groq_api_key", return_value="test-key"), patch("groq.Groq") as client:
            reply = self.generate("How much pesticide should I use?", intent="high_risk")
        self.assertEqual(reply.status, "safety_fallback")
        client.assert_not_called()

    def test_general_reply_uses_model_language_and_fictional_context(self):
        completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Check the sample field conditions first."))])
        groq_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=Mock(return_value=completion))
            )
        )
        with patch.dict(os.environ, {"GROQ_MODEL": "openai/gpt-oss-20b"}), \
             patch("bhomi.groq_ai.get_groq_api_key", return_value="test-key"), \
             patch("groq.Groq", return_value=groq_client) as client_class:
            reply = self.generate(history=[{"role": "user", "text": "Earlier question"}])

        self.assertEqual(reply.status, "ok")
        self.assertEqual(reply.model, "openai/gpt-oss-20b")
        self.assertEqual(reply.text, "Check the sample field conditions first.")
        client_class.assert_called_once_with(api_key="test-key", timeout=25.0, max_retries=0)
        request = groq_client.chat.completions.create.call_args.kwargs
        self.assertEqual(request["messages"][0]["role"], "system")
        self.assertIn("English only", request["messages"][0]["content"])
        self.assertIn('"is_demo": true', request["messages"][-1]["content"])
        self.assertNotIn("tools", request)

    def test_gujarati_reply_sets_gujarati_instruction(self):
        completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="પહેલા ખેતરની હાલત જુઓ."))])
        groq_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=Mock(return_value=completion))
            )
        )
        with patch("bhomi.groq_ai.get_groq_api_key", return_value="test-key"), \
             patch("groq.Groq", return_value=groq_client):
            reply = self.generate(language="gu")
        self.assertEqual(reply.status, "ok")
        self.assertIn("Gujarati only", groq_client.chat.completions.create.call_args.kwargs["messages"][0]["content"])

    def test_wrong_language_model_reply_is_rejected_for_local_fallback(self):
        completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Tomorrow will be sunny."))])
        groq_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=Mock(return_value=completion))
            )
        )
        with patch("bhomi.groq_ai.get_groq_api_key", return_value="test-key"), \
             patch("groq.Groq", return_value=groq_client):
            reply = self.generate(language="gu")
        self.assertEqual(reply.status, "language_mismatch")
        self.assertIsNone(reply.text)


if __name__ == "__main__":
    unittest.main()
