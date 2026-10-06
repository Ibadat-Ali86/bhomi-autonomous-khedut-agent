# BHOMI — Autonomous Khedut Agent

Gujarati-first product prototype for a client walkthrough, with English available as a secondary interface and assistant language. Use the language selector in the sidebar; Gujarati is selected by default. The app uses fictional fixtures. With a Groq API key, general chat replies use the configured Groq model; without one, reviewed local demo replies keep the walkthrough available. It does not connect to farmers, live weather, market prices, satellite data, or agronomy services.

## Requirements

- Python 3.11 or newer
- Core demo requires no API keys; Groq chat is optional
- Voice recognition downloads its multilingual model on first use
- Gujarati display uses fonts available in the browser/operating system

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-voice.txt  # enable microphone transcription
streamlit run app.py
```

To enable Groq replies, configure `GROQ_API_KEY` in the server environment or add this to the ignored `.streamlit/secrets.toml` file:

```toml
[groq]
api_key = "your-key"
```

Optionally set `GROQ_MODEL` in the server environment (default: `openai/gpt-oss-20b`). Do not put keys in source control, screenshots, or chat transcripts. The app does not load `.env` automatically.

Open the local URL printed by Streamlit. The bundled configuration binds to `127.0.0.1`, limits image uploads to 8 MB, and disables usage statistics. Select either fictional sample field in the sidebar.

## Demo walkthrough (3–5 minutes)

1. Open **શરૂઆત** (Practice guide) and complete the five practice steps. Switch to English from the sidebar to review the secondary language experience.
2. On **ખેતર**, switch between the sample cotton and wheat fields; point out the schematic boundary and sample labels.
3. Open **વાતચીત** and ask `આજે મારા ખેતરમાં શું કરવું?`, then ask `એ કેમ?` to show follow-up context.
4. Ask about irrigation, the weather sample, or the mandi sample. Read the source and date next to each answer.
5. Open **ફોટો તપાસ**. Upload a crop photo, read the privacy note, then click **AIથી ફોટો તપાસો / Analyze photo with AI**. With Groq configured, BHOMI returns a localized visual summary and approximate numbered areas. Without a photo, the illustrated sample cases remain available.
6. In **વાતચીત**, type in the composer or tap its microphone and ask a short question. The demo transcribes Gujarati or English, then lets you review and edit the transcript before sending it through the same contextual assistant as typed questions. With Groq configured, general replies in either mode use the selected Groq model. Beneath a reply, choose **જવાબનો અવાજ બનાવો / Generate reply audio** and then use the audio player. Gujarati replies use the Gujarati neural voice; English replies use an Indian English voice.
7. Close by explaining that language, agronomy, live data sources, privacy, and the pilot operating model need validation before production work.

## Voice behavior

The composer accepts typed questions and microphone recordings. For voice turns, local Whisper detects Gujarati or English and the answer follows the detected language; when detection is uncertain or transcription fails, the selected sidebar language is used as the fallback. The review panel shows which response language is selected before submission. Install `requirements-voice.txt` to enable local speech recognition; it pins PyAV below version 19 for compatibility with the current faster-whisper audio decoder. The multilingual `tiny` model loads on the first voice question and may download from Hugging Face then; that first request needs internet, disk space, and CPU time. Later requests reuse the loaded model. Audio is processed by the BHOMI app server and a temporary audio file is removed after transcription. The captured recording stays in Streamlit session memory only until you send or discard it. After confirmation, the transcript, recent chat turns, and fictional selected-field context are sent to Groq when configured; otherwise local reviewed replies are used. Do not enter real farmer data or use a remotely hosted demo with sensitive recordings. Gujarati regional vocabulary and English accuracy are not established for production.

## Crop photo review

Uploaded photos are validated, EXIF/location metadata is removed, and the image is resized before inference. The photo is sent to Groq only when the user clicks **Analyze photo with AI** and a server-side `GROQ_API_KEY` is configured. Set `GROQ_VISION_MODEL` separately from the text-only `GROQ_MODEL`; the default is `qwen/qwen3.8-27b`, which Groq documents as vision-capable. The model response is constrained and validated as JSON. Numbered boxes are approximate model-provided regions, not segmentation or proof that a leaf area is healthy or diseased. The result is a visual observation only, not a diagnosis or treatment recommendation. Photos and analysis results are kept in the active Streamlit session only; no image database or file archive is used. Do not upload identifiable people, real farm/location details, or sensitive photos to this demo. Review Groq's current data-handling terms before using real farmer images.

Replies remain visible as text. To hear one, click the audio-generation button and then play the generated MP3 in Streamlit's audio player. This uses the `edge-tts` client with Microsoft's online text-to-speech service and does not require another API key. Audio is generated only after the user clicks; the reply text is sent to that service at that point. A network connection is required, and service availability can change because `edge-tts` is a community client rather than Microsoft's supported SDK. Gujarati uses `gu-IN-DhwaniNeural`; English uses `en-IN-NeerjaNeural`. Generated MP3 data is kept in the current Streamlit session so reruns do not repeat synthesis. Keep real farmer data out of this demo. Model configuration is documented in `.env.example`; the app does not load `.env` automatically.

## Data and safety boundaries

- All farm profiles, field areas, coordinates, alerts, weather, prices, advisories, and crop illustrations are fictional. Every fixture record is marked `is_demo: true` and has a source label; dated records include `as_of` or `observed_at`.
- Field polygons are schematic coordinates and are not surveyed or used to identify a real parcel.
- Weather and mandi values are not current external observations. Prices are sample historical-looking values, not forecasts or guaranteed sale prices.
- Sample photo cases are illustrative. A submitted upload can be sent to Groq vision for approximate visible-area observations, but the model cannot diagnose disease, establish whole-crop health, or give a pesticide/fertilizer dose or product recommendation.
- The local intent router supplies a reviewed fallback and blocks high-risk or photo-diagnosis prompts from open-ended model generation. General Groq replies are bounded to the selected demo context and recent session turns; the model has no tools or access to live sources. Unsupported questions can receive brief general education, but should not be treated as verified agronomic advice.
- No account, GPS permission, persistent audio storage, public deployment, external data API, or production security boundary exists here.
- Groq says inference inputs/outputs are not retained by default, but may be temporarily logged for reliability or abuse monitoring for up to 30 days. Keep this prototype on fictional data and review the provider's current data controls before any real farmer use.

The SVG leaf artwork in `assets/` is original, locally drawn schematic demo art, not a photograph or crop reference. The brand mark is a local demo asset.

## Project layout

```text
app.py                  Streamlit interface and session-only journey
bhomi/assistant.py      Gujarati/Roman Gujarati routing and safe answer templates
bhomi/demo_data.py      Local fixture loading and validation
bhomi/map_view.py       Schematic unsurveyed boundary illustration
bhomi/voice.py          Cached local speech recognition for Gujarati/English questions
bhomi/groq_ai.py        Optional bounded Groq chat for typed and confirmed voice questions
bhomi/tts.py            On-demand online Gujarati/English reply audio generation
data/                    Fictional demo fixtures
assets/                  Local SVG logo and illustrative leaf cases
tests/                   Fixture, intent, follow-up, and safety checks
```

## Checks

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py bhomi tests
streamlit run app.py
```

The interactive checks are: change fields, ask a supported question, ask `એ કેમ?`, try an unsupported question, view both leaf cases, check source/date labels, record a microphone question in Gujarati and English, and use the reply speaker control. No deployment or production agronomy validation is claimed.

## Next phase after client approval

Validate Kheralu Gujarati and crop vocabulary with farmers and agronomists; agree who reviews advice; verify data rights and source freshness; set privacy, consent, and retention rules; then plan a secure opt-in pilot. Do not turn fixture values into live claims.
