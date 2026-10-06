import unittest

from bhomi.assistant import answer_question, route_intent
from bhomi.demo_data import load_demo_data


class IntentTests(unittest.TestCase):
    def setUp(self):
        data = load_demo_data()
        self.farm = data["farms"]["fields"][0]
        self.weather = data["weather"][0]
        self.price = data["prices"][0]
        self.alert = data["alerts"][0]
        self.advisory = data["advisories"][0]

    def test_supported_gujarati_and_roman_prompts(self):
        examples = {
            "નમસ્તે": "greeting",
            "આજે મારા ખેતરમાં શું કરવું?": "status",
            "માટી સૂકી છે, પાણી આપું?": "irrigation",
            "આવતીકાલનું હવામાન": "weather",
            "કપાસનો મંડી ભાવ": "prices",
            "મારું ખેતર નકશો": "field",
            "ચેતવણી સમજાવો": "alert",
            "પાન પર ડાઘ છે": "photo",
            "kem cho": "greeting",
            "aaje mara khetarma shu karvu?": "status",
            "varsad kevo che": "weather",
            "khetar ma pani aapu?": "irrigation",
            "cotton mandi bhav": "prices",
            "What should I do in my field today?": "status",
            "Should I irrigate today?": "irrigation",
            "What is tomorrow's weather?": "weather",
            "Show my field map": "field",
            "Explain the alert": "alert",
            "What are these spots on the leaf?": "photo",
            "How much pesticide should I use?": "high_risk",
        }
        for phrase, expected in examples.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(route_intent(phrase), expected)

    def test_follow_up_keeps_previous_topic(self):
        self.assertEqual(route_intent("એ કેમ?", "weather"), "weather")

    def test_unknown_follow_up_asks_clarification(self):
        self.assertEqual(route_intent("એ કેમ?"), "unclear")

    def test_unsafe_dosage_escalates_without_giving_amount(self):
        answer = answer_question("કપાસમાં કઈ દવા કેટલી નાખું?", self.farm, self.weather, self.price, self.alert, self.advisory)
        self.assertEqual(answer.intent, "high_risk")
        self.assertIn("KVK", answer.text_gu)
        self.assertNotIn("મિલીલીટર", answer.text_gu)

    def test_photo_answer_is_uncertain_and_has_no_prescription(self):
        answer = answer_question("પાન પર ડાઘ છે", self.farm, self.weather, self.price, self.alert, self.advisory)
        self.assertIn("નક્કી કરવા પૂરતું નથી", answer.text_gu)
        self.assertNotIn("છંટકાવ કરો", answer.text_gu)

    def test_english_response_is_complete_and_grounded(self):
        answer = answer_question("What is tomorrow's weather?", self.farm, self.weather, self.price, self.alert, self.advisory)
        self.assertIn("Light rain tomorrow", answer.text_en)
        self.assertIn("invented for the demo", answer.text_en)

    def test_english_dosage_request_escalates_safely(self):
        answer = answer_question("How much pesticide should I use?", self.farm, self.weather, self.price, self.alert, self.advisory)
        self.assertIn("agriculture officer", answer.text_en)
        self.assertNotIn("ml", answer.text_en.lower())


if __name__ == "__main__":
    unittest.main()
