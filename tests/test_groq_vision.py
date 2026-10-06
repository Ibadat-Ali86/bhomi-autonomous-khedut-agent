import base64
import json
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from bhomi.groq_vision import (
    PhotoInputError,
    VisionReply,
    VisualRegion,
    _validated_result,
    prepare_uploaded_photo,
    review_crop_photo,
)


def sample_jpeg() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (96, 64), (76, 129, 62)).save(buffer, format="JPEG")
    return buffer.getvalue()


class GroqVisionTests(unittest.TestCase):
    def test_uploaded_photo_is_oriented_metadata_stripped_jpeg(self):
        prepared = prepare_uploaded_photo(sample_jpeg())
        self.assertTrue(prepared.jpeg_bytes.startswith(b"\xff\xd8"))
        self.assertEqual((prepared.width, prepared.height), (96, 64))
        with Image.open(BytesIO(prepared.jpeg_bytes)) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertFalse(image.getexif())

    def test_rejects_invalid_and_oversized_uploads(self):
        with self.assertRaises(PhotoInputError):
            prepare_uploaded_photo(b"not an image")
        with patch("bhomi.groq_vision.MAX_UPLOAD_BYTES", 10):
            with self.assertRaises(PhotoInputError) as error:
                prepare_uploaded_photo(sample_jpeg())
        self.assertEqual(str(error.exception), "too_large")

    def test_response_validation_keeps_only_bounded_regions(self):
        result = _validated_result(json.dumps({
            "is_crop": True,
            "summary": "પાન પર એક દેખાતો ડાઘ છે.",
            "regions": [
                {"label": "concerning", "bbox": [120, 140, 420, 460], "observation": "અહીં રંગનો બદલાવ દેખાય છે."},
                {"label": "diagnosis", "bbox": [0, 0, 1000, 1000], "observation": "આ રોગ છે."},
                {"label": "unclear", "bbox": [-10, 0, 50, 100], "observation": "અસ્પષ્ટ."},
            ],
        }, ensure_ascii=False), "gu", "qwen/qwen3.8-27b")
        self.assertEqual(result.status, "ok")
        self.assertEqual(len(result.regions), 1)
        self.assertEqual(result.regions[0].bbox, (120, 140, 420, 460))

    def test_groq_request_contains_the_photo_as_a_multimodal_input(self):
        prepared = prepare_uploaded_photo(sample_jpeg())
        result_payload = {
            "is_crop": True,
            "summary": "પાનના ભાગમાં રંગનો બદલાવ દેખાય છે.",
            "regions": [{
                "label": "concerning",
                "bbox": [100, 100, 500, 500],
                "observation": "આ વિસ્તારમાં રંગનો બદલાવ છે.",
            }],
        }
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(result_payload, ensure_ascii=False)))]
        )
        with patch("bhomi.groq_vision.get_groq_api_key", return_value="test-key"), patch(
            "groq.Groq", return_value=client
        ):
            result = review_crop_photo(prepared, "gu", "કપાસ")

        self.assertEqual(result.status, "ok")
        call = client.chat.completions.create.call_args.kwargs
        self.assertEqual(call["model"], "qwen/qwen3.8-27b")
        user_content = call["messages"][1]["content"]
        image_url = next(item["image_url"]["url"] for item in user_content if item["type"] == "image_url")
        self.assertTrue(image_url.startswith("data:image/jpeg;base64,"))
        decoded = base64.b64decode(image_url.split(",", 1)[1])
        self.assertTrue(decoded.startswith(b"\xff\xd8"))
        self.assertEqual(call["response_format"], {"type": "json_object"})

    def test_missing_key_does_not_make_a_provider_call(self):
        photo = prepare_uploaded_photo(sample_jpeg())
        with patch("bhomi.groq_vision.get_groq_api_key", return_value=""), patch("groq.Groq") as groq_client:
            result = review_crop_photo(photo, "en", "cotton")
        self.assertEqual(result.status, "not_configured")
        groq_client.assert_not_called()

    def test_photo_page_explains_submission_boundary_without_upload(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path))
        app.session_state["page"] = "photo"
        app.session_state["language"] = "English"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Analyze photo with AI", " ".join(item.value for item in app.caption))
        self.assertTrue(app.get_by_key("crop_upload"))

    def test_submitting_a_photo_renders_annotated_gujarati_review(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path))
        app.session_state["page"] = "photo"
        app.session_state["language"] = "ગુજરાતી"
        reply = VisionReply(
            status="ok",
            model="qwen/qwen3.8-27b",
            summary="પાનના ભાગમાં રંગનો બદલાવ દેખાય છે.",
            is_crop=True,
            regions=(VisualRegion("concerning", (120, 150, 480, 510), "અહીં રંગનો બદલાવ છે."),),
        )
        with patch("bhomi.groq_ai.groq_is_configured", return_value=True), patch(
            "bhomi.groq_vision.review_crop_photo", return_value=reply
        ) as review_photo:
            app.run()
            app.file_uploader(key="crop_upload").set_value(("leaf.jpg", sample_jpeg(), "image/jpeg")).run()
            app.button(key="analyze_crop_photo").click().run()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(review_photo.call_args.args[1:], ("gu", "કપાસ"))
        self.assertEqual(app.session_state["crop_photo_review"]["reply"].summary, reply.summary)
        self.assertIn("પાકના ફોટા", " ".join(item.value for item in app.markdown))

    def test_uploaded_photo_explains_missing_groq_key_and_disables_submit(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path))
        app.session_state["page"] = "photo"
        app.session_state["language"] = "English"
        with patch("bhomi.groq_ai.groq_is_configured", return_value=False):
            app.run()
            app.file_uploader(key="crop_upload").set_value(("leaf.jpg", sample_jpeg(), "image/jpeg")).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.button(key="analyze_crop_photo").disabled)
        self.assertTrue(any("GROQ_API_KEY" in warning.value for warning in app.warning))


if __name__ == "__main__":
    unittest.main()
