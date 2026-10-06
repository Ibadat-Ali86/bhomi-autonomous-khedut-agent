"""Shared view helpers for cards, data provenance and Gujarati speech playback."""
import html
import json

import streamlit as st


def card(title: str, value: str, detail: str, label: str = "નમૂના ડેટા", tone: str = "green") -> None:
    st.markdown(
        f'<section class="metric-card {tone}"><div class="card-top"><span>{html.escape(title)}</span>'
        f'<span class="pill">{html.escape(label)}</span></div><strong>{html.escape(value)}</strong>'
        f'<div class="card-detail">{html.escape(detail)}</div></section>',
        unsafe_allow_html=True,
    )


def speech_player(text: str, key: str, language: str = "gu") -> None:
    safe_text = json.dumps(text, ensure_ascii=False)
    locale = "en-IN" if language == "en" else "gu-IN"
    button_text = "Listen to reply" if language == "en" else "જવાબ સાંભળો"
    available = "Tap to hear this reply in English." if language == "en" else "જવાબ ગુજરાતીમાં સાંભળવા અહીં દબાવો."
    unsupported = "Speech playback is unavailable in this browser." if language == "en" else "આ બ્રાઉઝરમાં અવાજ ઉપલબ્ધ નથી."
    unavailable = "No compatible English voice is available on this device." if language == "en" else "આ ઉપકરણમાં ગુજરાતી અવાજ ઉપલબ્ધ નથી."
    playing = "Playing reply in English." if language == "en" else "ગુજરાતીમાં જવાબ વગાડી રહ્યો છે."
    st.iframe(f'''<!doctype html><meta charset="utf-8">
      <button id="play" data-instance="{html.escape(key, quote=True)}" aria-label="{html.escape(button_text, quote=True)}">🔊 {html.escape(button_text)}</button>
      <span id="status" aria-live="polite">{html.escape(available)}</span>
      <script>
      const text = {safe_text};
      const btn = document.getElementById('play');
      const status = document.getElementById('status');
      btn.onclick = () => {{
        if (!('speechSynthesis' in window)) {{ status.textContent = '{unsupported}'; return; }}
        const speak = () => {{
          const voices = speechSynthesis.getVoices();
          const voice = voices.find(v => v.lang.toLowerCase() === '{locale.lower()}') || voices.find(v => v.lang.toLowerCase().startsWith('{language}'));
          if (!voice) {{ status.textContent = '{unavailable}'; return; }}
          speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = '{locale}'; utterance.voice = voice; utterance.rate = 0.96;
          utterance.onerror = () => {{ status.textContent = '{unsupported}'; }};
          speechSynthesis.speak(utterance); status.textContent = '{playing}';
        }};
        if (speechSynthesis.getVoices().length) speak();
        else {{ status.textContent = 'Loading voice…'; speechSynthesis.onvoiceschanged = speak; }}
      }};
      </script><style>body{{font:13px sans-serif;color:#26342b;margin:4px;display:flex;align-items:center;flex-wrap:wrap;gap:8px}}button{{padding:9px 14px;border:1px solid #cbd4c2;border-radius:12px;background:#e7eedc;color:#26342b;cursor:pointer;font:600 13px sans-serif}}button:hover{{background:#dbe7cc}}#status{{color:#667267}}</style>''', height=58, tab_index=0, alt=button_text)
