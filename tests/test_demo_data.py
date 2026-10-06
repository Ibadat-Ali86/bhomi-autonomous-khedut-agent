import unittest

from bhomi.demo_data import DemoDataError, load_demo_data, validate_data


class DemoDataTests(unittest.TestCase):
    def test_all_local_fixtures_load_and_validate(self):
        data = load_demo_data()
        self.assertEqual(len(data["farms"]["fields"]), 2)
        self.assertTrue(all(farm["is_demo"] for farm in data["farms"]["fields"]))

    def test_missing_demo_label_is_rejected(self):
        data = load_demo_data()
        data["weather"][0]["is_demo"] = False
        with self.assertRaises(DemoDataError):
            validate_data(data)

    def test_missing_provenance_date_is_rejected(self):
        data = load_demo_data()
        del data["prices"][0]["as_of"]
        with self.assertRaises(DemoDataError):
            validate_data(data)

    def test_bilingual_fields_are_required(self):
        data = load_demo_data()
        del data["weather"][0]["summary_en"]
        with self.assertRaises(DemoDataError):
            validate_data(data)


if __name__ == "__main__":
    unittest.main()
