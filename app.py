from __future__ import annotations

import html
from io import BytesIO

import streamlit as st

from bhomi.assistant import Answer, answer_question
from bhomi.config import APP_TITLE, ASSET_DIR, COLORS
from bhomi.demo_data import DemoDataError, load_demo_data
from bhomi.i18n import LEGACY_NAV, NAV_IDS, data_text, tr
from bhomi.map_view import polygon_svg
from bhomi.ui import card, speech_player
from bhomi.voice import transcribe_locally


st.set_page_config(page_title=APP_TITLE, page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
:root{{--soil:{COLORS['soil']};--paper:{COLORS['paper']};--ink:{COLORS['ink']};--muted:{COLORS['muted']};--leaf:{COLORS['leaf']};--soft:{COLORS['leaf_light']};--wheat:{COLORS['wheat']};--line:{COLORS['line']};--background-color:{COLORS['soil']};--secondary-background-color:{COLORS['paper']};--text-color:{COLORS['ink']};--primary-color:{COLORS['leaf']};color-scheme:light}}
html,body,[class*="css"]{{font-family:'Noto Sans Gujarati','Nirmala UI','Shruti',sans-serif;color:var(--ink)}}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:var(--soil)!important;color:var(--ink)!important}}
[data-testid="stMainBlockContainer"]{{max-width:1320px;padding-top:2rem;padding-bottom:3rem}}
[data-testid="stHeader"]{{background:transparent}}
[data-testid="stToolbar"],[data-testid="stToolbar"] button{{color:var(--ink)!important}}
[data-testid="stSidebar"]{{background:#eeebdf!important;border-right:1px solid var(--line);color:var(--ink)!important}}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span,[data-testid="stSidebar"] strong{{color:var(--ink)!important}}
h1,h2,h3,h4,h5{{color:var(--ink)!important}} p{{color:var(--muted)!important}}
label,[data-testid="stWidgetLabel"],[data-testid="stCaptionContainer"]{{color:var(--muted)!important}}
.stSelectbox [data-baseweb="select"]>div{{background:var(--paper)!important;border-color:var(--line)!important;color:var(--ink)!important}}
[role="listbox"],[role="option"]{{background:var(--paper)!important;color:var(--ink)!important}}
input,textarea{{background:var(--paper)!important;color:var(--ink)!important;border-color:var(--line)!important}}
[data-testid="stFileUploaderDropzone"]{{background:var(--paper)!important;border-color:var(--line)!important;color:var(--ink)!important}}
[data-testid="stFileUploaderDropzone"] *{{color:var(--ink)!important}}
[data-testid="stAlert"]{{background:var(--paper);color:var(--ink)}}
.hero{{background:var(--paper);border:1px solid var(--line);border-left:5px solid var(--leaf);border-radius:20px;padding:24px 28px;margin:4px 0 14px;box-shadow:0 8px 28px rgba(38,52,43,.045)}}
.hero-eyebrow{{color:var(--leaf);font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px}}
.hero h1{{font-size:clamp(26px,4vw,38px);color:var(--ink)!important;margin:0 0 4px;line-height:1.35}} .hero p{{color:var(--muted)!important;margin:0;line-height:1.65}}
.demo-banner{{background:#f7edcf;border-left:5px solid var(--wheat);border-radius:10px;padding:12px 16px;margin:10px 0 18px;color:#554620}}
.metric-card{{background:var(--paper);border:1px solid var(--line);border-top:3px solid var(--leaf);border-radius:16px;padding:16px 17px;min-height:137px;margin-bottom:12px;box-shadow:0 6px 20px rgba(38,52,43,.035)}}
.metric-card.blue{{border-top-color:var(--water)}} .metric-card.gold{{border-top-color:var(--wheat)}}
.metric-card strong{{display:block;font-size:22px;color:var(--ink);margin:17px 0 5px;line-height:1.4}} .card-top{{display:flex;align-items:center;justify-content:space-between;gap:8px;color:var(--muted);font-size:14px}}
.pill{{display:inline-block;background:var(--soft);color:var(--leaf);border-radius:999px;padding:4px 9px;font-size:11px;white-space:nowrap}}
.card-detail{{font-size:13px;color:var(--muted);line-height:1.6}} .section-title{{font-size:21px;font-weight:700;margin:20px 0 8px}}
.map-wrap{{background:var(--paper);border:1px solid var(--line);border-radius:17px;padding:10px;margin:6px 0 14px}} .map-wrap svg{{display:block;width:100%;height:auto}}
.note{{color:var(--muted);font-size:13px}} .alert-card{{background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--wheat);border-radius:12px;padding:13px 15px;margin:8px 0}}
.stButton>button{{border-radius:11px;min-height:42px;background:var(--paper)!important;color:var(--ink)!important;border:1px solid var(--line);font-weight:600;transition:background .15s ease,border-color .15s ease,transform .15s ease}} .stButton>button:hover{{border-color:var(--leaf)!important;background:var(--soft)!important;color:var(--ink)!important;transform:translateY(-1px)}} .stButton>button[kind="primary"]{{background:var(--leaf)!important;border-color:var(--leaf)!important;color:#fff!important}} .stButton>button[kind="primary"]:hover{{background:#3e5a2f!important;color:#fff!important}}
.stRadio [role="radiogroup"]{{gap:8px}} .stRadio [role="radio"]{{border-radius:10px}}
.stChatMessage{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin:8px 0}}
.stChatInput textarea{{border-radius:14px!important}} .stExpander{{background:var(--paper);border-color:var(--line)!important;border-radius:14px!important}}
.section-title{{color:var(--ink)}} .card-detail{{overflow-wrap:anywhere}}
.step{{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:15px;margin:8px 0}}
@media(max-width:760px){{.hero{{padding:18px}}.metric-card{{min-height:unset}}[data-testid="stHorizontalBlock"]{{flex-wrap:wrap!important;gap:.5rem!important}}[data-testid="stHorizontalBlock"]>[data-testid="column"]{{width:100%!important;flex:1 1 100%!important;min-width:100%!important}}}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{scroll-behavior:auto!important;animation-duration:.01ms!important;transition-duration:.01ms!important}}}}
</style>
""", unsafe_allow_html=True)


try:
    DATA = load_demo_data()
except (OSError, ValueError, DemoDataError):
    st.error("નમૂના માહિતી ખોલી શકાઈ નથી. કૃપા કરીને પ્રોજેક્ટની data/ ફાઇલો તપાસો.")
    st.stop()

FARMS = DATA["farms"]["fields"]
FARMER = DATA["farms"]["farmer"]
if "field_id" not in st.session_state:
    st.session_state.field_id = FARMS[0]["id"]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "completed_steps" not in st.session_state:
    st.session_state.completed_steps = set()
if "page" not in st.session_state:
    st.session_state.page = "farm"
if st.session_state.page not in NAV_IDS:
    st.session_state.page = LEGACY_NAV.get(st.session_state.page, "farm")
if "pending_page" in st.session_state:
    pending_page = st.session_state.pop("pending_page")
    st.session_state.page = LEGACY_NAV.get(pending_page, pending_page if pending_page in NAV_IDS else "farm")
if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = ""

language = "en" if st.session_state.get("language", "ગુજરાતી") == "English" else "gu"
farm = next((f for f in FARMS if f["id"] == st.session_state.field_id), FARMS[0])
weather = next(r for r in DATA["weather"] if r["field_id"] == farm["id"])
price = next(r for r in DATA["prices"] if r["crop_gu"] == farm["crop_gu"])
alert = next(r for r in DATA["alerts"] if r["field_id"] == farm["id"])
advisory = next(r for r in DATA["advisories"] if r["crop_gu"] == farm["crop_gu"])

with st.sidebar:
    st.markdown("## 🌿 BHOMI")
    st.caption(tr("sidebar_tagline", language))
    st.radio(tr("language", language), ["ગુજરાતી", "English"], horizontal=True, key="language")
    st.caption(tr("language_note", language))
    st.markdown(f"**{tr('farmer', language)}:** {data_text(FARMER, 'label_gu', language)}")
    field_id = st.selectbox(tr("select_field", language), [f["id"] for f in FARMS], index=[f["id"] for f in FARMS].index(farm["id"]), format_func=lambda value: next(data_text(f, "name_gu", language) for f in FARMS if f["id"] == value), key="field_selector")
    if field_id != st.session_state.field_id:
        st.session_state.field_id = field_id
        st.rerun()
    st.divider()
    st.radio(tr("navigation", language), NAV_IDS, format_func=lambda value: tr(f"nav_{value}", language), key="page", label_visibility="visible")
    st.divider()
    st.caption(tr("privacy", language))

farmer_name = html.escape(data_text(FARMER, "label_gu", language))
farm_name = html.escape(data_text(farm, "name_gu", language))
crop_name = html.escape(data_text(farm, "crop_gu", language))
location = html.escape(data_text(FARMER, "location_gu", language))
eyebrow = "KHERALU FIELD ASSISTANT · PROTOTYPE" if language == "en" else "ખેરાલુ ખેડૂત સહાયક · પ્રોટોટાઇપ"
st.markdown(f"<div class='hero'><div class='hero-eyebrow'>{eyebrow}</div><h1>{tr('greeting', language)}, {farmer_name}</h1><p>{location} · {farm_name} · {crop_name} · {tr('assistant_tagline', language)}</p></div>", unsafe_allow_html=True)
st.markdown(f"<div class='demo-banner'><strong>{'DEMO MODE' if language == 'en' else 'ડેમો મોડ'}</strong> · {tr('demo_banner', language).split(' · ', 1)[1]}</div>", unsafe_allow_html=True)


def submit_question(question: str, input_mode: str = "text") -> Answer:
    previous = next((m["intent"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
    result = answer_question(question, farm, weather, price, alert, advisory, previous)
    provenance = {
        "status": (advisory, "source_label", "as_of"),
        "irrigation": (weather, "source_label", "as_of"),
        "weather": (weather, "source_label", "as_of"),
        "prices": (price, "source_label", "as_of"),
        "field": (farm, "source_label", "observed_at"),
        "alert": (alert, "source_label", "as_of"),
    }.get(result.intent)
    source_record, source_key, date_key = provenance if provenance else ({}, "", "")
    source_gu = source_record.get(source_key, result.source_label) if source_key else result.source_label
    source_en = data_text(source_record, source_key, "en") if provenance else ("Safety guidance" if result.intent in {"photo", "high_risk"} else "")
    as_of_gu = source_record.get(date_key, result.as_of) if date_key else result.as_of
    as_of_en = data_text(source_record, date_key, "en") if date_key else None
    st.session_state.messages.extend([
        {"role": "user", "text": question, "input_mode": input_mode},
        {"role": "assistant", "text": result.text_gu, "text_gu": result.text_gu, "text_en": result.text_en, "intent": result.intent, "source": source_gu, "source_en": source_en, "as_of": as_of_gu, "as_of_en": as_of_en, "evidence": result.evidence, "follow_up": result.follow_up, "follow_up_en": result.follow_up_en, "demo": result.is_demo},
    ])
    st.session_state.completed_steps.add("chat")
    return result


def render_answer(answer: dict, index: int) -> None:
    with st.chat_message(answer["role"]):
        answer_text = answer.get(f"text_{language}", answer["text"])
        st.markdown(answer_text)
        if answer["role"] == "user" and answer.get("input_mode") == "voice":
            st.caption("Voice transcript" if language == "en" else "અવાજમાંથી લખાણ")
        if answer["role"] == "assistant":
            if answer.get("source"):
                source_label = answer.get("source_en", answer["source"]) if language == "en" else answer["source"]
                date = answer.get("as_of_en", answer.get("as_of")) if language == "en" else answer.get("as_of")
                provenance = f"{source_label} · {date or ('General guidance' if language == 'en' else 'સામાન્ય માર્ગદર્શન')}"
                st.caption(provenance + (" · Sample" if language == "en" and answer.get("demo") else (" · નમૂનો" if answer.get("demo") else "")))
            follow_up = answer.get("follow_up_en", answer.get("follow_up")) if language == "en" else answer.get("follow_up")
            if follow_up:
                st.caption(("Next: " if language == "en" else "આગળ: ") + follow_up)
            speech_player(answer_text, f"speech-{index}", language)


def show_photo_view():
    st.markdown(f"## {tr('photo_title', language)}")
    st.caption(tr("photo_description", language))
    case = st.selectbox(tr("demo_case", language), DATA["crop_cases"], format_func=lambda item: data_text(item, "title_gu", language), key="crop_case")
    uploaded = st.file_uploader(tr("optional_upload", language), type=["jpg", "jpeg", "png", "webp"], help=tr("upload_help", language))
    cols = st.columns(2)
    with cols[0]:
        st.image(str(ASSET_DIR / case["image"]), caption=data_text(case, "title_gu", language), width="stretch")
    with cols[1]:
        if uploaded:
            try:
                from PIL import Image
                image = Image.open(BytesIO(uploaded.getvalue()))
                if image.width * image.height > 20_000_000:
                    st.warning(tr("image_too_large", language))
                else:
                    st.image(image, caption=tr("upload_preview", language), width="stretch")
            except Exception:
                st.warning(tr("image_invalid", language))
        else:
            st.markdown(f"<div class='step'>{tr('upload_unavailable', language)}</div>", unsafe_allow_html=True)
    st.info(f"**{tr('sample_triage', language)}:** {data_text(case, 'result_gu', language)}\n\n{tr('low_confidence', language)}")
    st.caption(f"{data_text(case, 'source_label', language)} · {tr('demo_seen', language)}")
    if st.button(tr("photo_done", language), type="primary"):
        st.session_state.completed_steps.add("photo")
        st.success(tr("step_done", language))


page = st.session_state.page
if page == "farm":
    st.markdown(f"<div class='section-title'>{html.escape(data_text(farm, 'name_gu', language))} · {tr('field_status', language)}</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: card(tr("crop", language), data_text(farm, "crop_gu", language), data_text(farm, "stage_gu", language), tr("card_sample", language))
    with c2: card(tr("area", language), f"{farm['area_acres']} acres" if language == "en" else f"{farm['area_acres']} એકર", tr("sample_area", language), tr("card_sample", language))
    with c3: card(tr("weather", language), data_text(weather, "summary_gu", language), f"{data_text(weather, 'source_label', language)} · {data_text(weather, 'as_of', language)}", tr("card_sample", language), tone="blue")
    with c4: card(tr("irrigation_cue", language), tr("check_first", language), tr("soil_not_measured", language), tr("card_sample", language), tone="gold")
    left, right = st.columns([1.15, .85])
    with left:
        st.markdown(f"<div class='section-title'>{tr('field_map', language)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='map-wrap'>{polygon_svg(farm, language=language)}</div>", unsafe_allow_html=True)
        st.caption(tr("map_disclaimer", language))
        if st.button(tr("mark_map_seen", language), key="field_seen"):
            st.session_state.completed_steps.add("field")
            st.success(tr("map_done", language))
    with right:
        st.markdown(f"<div class='section-title'>{tr('today_cue', language)}</div>", unsafe_allow_html=True)
        with st.expander(tr("why_cue", language), expanded=True):
            st.write(data_text(advisory, "reason_gu", language))
            st.caption(f"{data_text(advisory, 'source_label', language)} · {data_text(advisory, 'as_of', language)}")
            if st.button(tr("understood", language), key="why_seen"):
                st.session_state.completed_steps.add("status")
        st.markdown(f"<div class='alert-card'><strong>{html.escape(data_text(alert, 'title_gu', language))}</strong><div class='card-detail'>{html.escape(data_text(alert, 'reason_gu', language))}</div><span class='note'>{html.escape(data_text(alert, 'source_label', language))} · {data_text(alert, 'as_of', language)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='alert-card'><strong>{tr('recent_activity', language)}</strong><div>{html.escape(data_text(farm, 'recent_activity_gu', language))}</div><span class='note'>{html.escape(data_text(farm, 'source_label', language))} · {data_text(farm, 'observed_at', language)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='alert-card'><strong>{tr('sample_price', language)}</strong><div>{data_text(price, 'crop_gu', language)} · ₹{price['price_rupees_per_quintal']:,} {tr('price_unit', language)}</div><span class='note'>{data_text(price, 'market_gu', language)} · {data_text(price, 'source_label', language)} · {data_text(price, 'as_of', language)}</span></div>", unsafe_allow_html=True)
        if st.button(tr("sources_seen", language), key="data_seen"):
            st.session_state.completed_steps.add("sources")
    st.markdown(f"<div class='section-title'>{tr('quick_questions', language)}</div>", unsafe_allow_html=True)
    prompt_cols = st.columns(4)
    selected_crop = data_text(farm, "crop_gu", language)
    price_prompt = f"What is the {selected_crop} market price?" if language == "en" else f"{selected_crop}નો મંડી ભાવ કેટલો?"
    prompts = [tr("prompt_status", language), tr("prompt_water", language), tr("prompt_weather", language), price_prompt]
    for i, prompt in enumerate(prompts):
        if prompt_cols[i].button(prompt, key=f"quick-{i}", width="stretch"):
            submit_question(prompt)
            st.session_state.pending_page = "chat"
            st.rerun()
elif page == "chat":
    st.markdown(f"## {tr('chat_title', language)}")
    st.caption(tr("chat_description", language))
    if st.session_state.messages and st.button(tr("clear_chat", language), icon=":material/delete_sweep:"):
        st.session_state.messages = []
        st.rerun()
    if not st.session_state.messages:
        st.info(tr("chat_example", language))
    for idx, message in enumerate(st.session_state.messages):
        render_answer(message, idx)
    st.caption(tr("voice_footer", language))
    prompt = st.chat_input(
        tr("chat_placeholder", language),
        accept_audio=True,
        audio_sample_rate=16000,
        key="assistant_composer",
    )
    if prompt:
        question = prompt.text.strip()
        input_mode = "text"
        if prompt.audio:
            with st.spinner(tr("transcribing", language)):
                transcript, state = transcribe_locally(prompt.audio.getvalue(), language)
            if transcript:
                question = transcript
                input_mode = "voice"
            elif not question:
                st.error(tr(f"voice_{state}", language))
        if question:
            submit_question(question, input_mode)
            st.rerun()
elif page == "photo":
    show_photo_view()
else:
    st.markdown(f"## {tr('guide_title', language)}")
    st.write(tr("guide_description", language))
    if st.session_state.get("guide_skipped"):
        st.info(tr("guide_skipped", language))
    steps = [
        ("chat", "step_chat", "step_chat_detail", "chat"),
        ("field", "step_field", "step_field_detail", "farm"),
        ("status", "step_status", "step_status_detail", "farm"),
        ("photo", "step_photo", "step_photo_detail", "photo"),
        ("sources", "step_sources", "step_sources_detail", "farm"),
    ]
    for number, (key, title_key, detail_key, destination) in enumerate(steps, start=1):
        checked = key in st.session_state.completed_steps
        st.markdown(f"<div class='step'><strong>{'✓' if checked else f'{number:02d}'} · {tr(title_key, language)}</strong><div class='card-detail'>{tr(detail_key, language)}</div></div>", unsafe_allow_html=True)
        if st.button(tr("completed" if checked else "open_step", language), key=f"guide-{key}"):
            st.session_state.pending_page = destination
            st.rerun()
    st.progress(len(st.session_state.completed_steps) / len(steps), text=f"{len(st.session_state.completed_steps)} / {len(steps)} {tr('progress', language)}")
    g1, g2 = st.columns(2)
    if g1.button(tr("skip_practice", language)):
        st.session_state.guide_skipped = True
        st.rerun()
    if g2.button(tr("restart", language)):
        st.session_state.completed_steps = set()
        st.session_state.guide_skipped = False
        st.rerun()
