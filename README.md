# BHOMI — Autonomous Khedut Agent

Gujarati-first local product prototype for a client walkthrough, with English available as a secondary interface and assistant language. Use the language selector in the sidebar; Gujarati is selected by default. The app runs on fictional fixtures and deterministic response templates. It does not connect to farmers, live weather, market prices, satellite data, agronomy services, or a cloud AI model.

## Requirements

- Python 3.11 or newer
- Core demo requires no API keys; voice recognition downloads its model on first use
- Gujarati display uses fonts available in the browser/operating system

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-voice.txt  # enable microphone transcription
streamlit run app.py
```

Open the local URL printed by Streamlit. The bundled configuration binds to `127.0.0.1`, limits image uploads to 8 MB, and disables usage statistics. Select either fictional sample field in the sidebar.

## Demo walkthrough (3–5 minutes)

1. Open **શરૂઆત** (Practice guide) and complete the five practice steps. Switch to English from the sidebar to review the secondary language experience.
2. On **ખેતર**, switch between the sample cotton and wheat fields; point out the schematic boundary and sample labels.
3. Open **વાતચીત** and ask `આજે મારા ખેતરમાં શું કરવું?`, then ask `એ કેમ?` to show follow-up context.
4. Ask about irrigation, the weather sample, or the mandi sample. Read the source and date next to each answer.
5. Open **ફોટો તપાસ**. Show the illustrated leaf cases and the uncertainty wording. An uploaded image is preview-only and is not sent to a model.
6. In **વાતચીત**, type in the composer or tap its microphone and ask a short question. The demo transcribes Gujarati or English and displays the recognized words in the chat. Tap **જવાબ સાંભળો / Listen to reply** beneath an answer to hear it in the selected language.
7. Close by explaining that language, agronomy, live data sources, privacy, and the pilot operating model need validation before production work.

## Voice behavior

The composer accepts typed questions and microphone recordings. Install `requirements-voice.txt` to enable speech recognition. The multilingual `tiny` model loads on the first voice question and may download from Hugging Face then; that first request needs internet, disk space, and CPU time. Later requests reuse the loaded model. Audio is processed by the BHOMI app server and removed after transcription; this demo does not call a third-party speech API. Do not send sensitive recordings to a remotely hosted demo. Gujarati regional vocabulary and English accuracy are not established for production.

Replies remain visible as text and include a speaker button. Playback uses the browser's installed voice for the selected language. Browsers require a user tap to start speech, and Gujarati playback depends on a Gujarati voice being installed. If a compatible voice is unavailable, the text reply remains available. Model configuration is documented in `.env.example`; the app does not load `.env` automatically.

## Data and safety boundaries

- All farm profiles, field areas, coordinates, alerts, weather, prices, advisories, and crop illustrations are fictional. Every fixture record is marked `is_demo: true` and has a source label; dated records include `as_of` or `observed_at`.
- Field polygons are schematic coordinates and are not surveyed or used to identify a real parcel.
- Weather and mandi values are not current external observations. Prices are sample historical-looking values, not forecasts or guaranteed sale prices.
- Photo triage is a fixed explanatory sample. It does not inspect an upload or diagnose disease. It gives no pesticide/fertilizer dose or product recommendation.
- The assistant is a deterministic keyword router with bounded local templates, not an autonomous LLM agent. Unsupported and high-risk requests receive clarification or expert escalation.
- No account, GPS permission, persistent audio storage, public deployment, external data API, or production security boundary exists here.

The SVG leaf artwork in `assets/` is original, locally drawn schematic demo art, not a photograph or crop reference. The brand mark is a local demo asset.

## Project layout

```text
app.py                  Streamlit interface and session-only journey
bhomi/assistant.py      Gujarati/Roman Gujarati routing and safe answer templates
bhomi/demo_data.py      Local fixture loading and validation
bhomi/map_view.py       Schematic unsurveyed boundary illustration
bhomi/voice.py          Cached local speech recognition for Gujarati/English questions
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
