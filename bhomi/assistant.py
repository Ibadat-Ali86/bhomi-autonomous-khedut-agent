"""Bounded Gujarati intent router; answers are templates grounded in fixtures."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Answer:
    text_gu: str
    intent: str
    evidence: list[str] = field(default_factory=list)
    source_label: str = "BHOMI ડેમો"
    as_of: str | None = None
    confidence: str = "મર્યાદિત"
    is_demo: bool = True
    follow_up: str = "તમને કઈ માહિતી વધુ જોઈએ?"
    text_en: str = ""
    follow_up_en: str = "What would you like to know next?"


def _contains(text: str, groups: tuple[tuple[str, ...], ...]) -> bool:
    return any(any(word in text for word in group) for group in groups)


def route_intent(question: str, previous_intent: str | None = None) -> str:
    q = " ".join(question.lower().strip().split())
    if not q:
        return "unclear"
    if _contains(q, (("દવા", "જંતુનાશક", "છંટકાવ", "ખાતર", "dosage", "dose", "pesticide", "fertilizer", "medicine", "chemical", "spray", "how much"),)):
        return "high_risk"
    if q in {"hi", "hey", "hello", "નમસ્તે", "kem cho", "namaste"} or _contains(q, (("નમસ્તે", "કેમ છો", "હેલો", "hello", "kem cho", "namaste", "hi "),)):
        return "greeting"
    if _contains(q, (("ભાવ", "મંડી", "બજાર", "price", "mandi", "bhav", "market"),)):
        return "prices"
    if _contains(q, (("હવામાન", "વરસાદ", "weather", "rain", "varsad"),)):
        return "weather"
    if _contains(q, (("પાણી", "પિયત", "સિંચાઈ", "irrigation", "irrigate", "water", "pani", "piyat"),)):
        return "irrigation"
    if _contains(q, (("ચેતવણી", "alert", "warning", "સૂચના"),)):
        return "alert"
    if _contains(q, (("ફોટો", "પાન", "ડાઘ", "રોગ", "દેખાય", "photo", "leaf", "spots", "spot", "disease"),)):
        return "photo"
    if _contains(q, (("અવસ્થા", "વૃદ્ધિ", "ફૂલ", "ક્યારે", "પાક", "શું કરવું", "આજે", "crop", "stage", "today", "status", "should", "do in my", "su karvu", "atyare", "aaje", "karvu", "fasal"),)):
        return "status"
    if _contains(q, (("નકશો", "ખેતર ક્યાં", "સીમા", "map", "field history", "history", "khetar kya", "naksho", "field", "farm", "plot", "boundary"),)):
        return "field"
    if _contains(q, (("એ કેમ", "શા માટે", "kem", "why", "અને પછી"),)):
        return previous_intent if previous_intent in {"status", "irrigation", "weather", "prices", "photo", "alert"} else "unclear"
    return "unsupported"


def answer_question(question: str, farm: dict[str, Any], weather: dict[str, Any], price: dict[str, Any], alert: dict[str, Any], advisory: dict[str, Any], previous_intent: str | None = None) -> Answer:
    intent = route_intent(question, previous_intent)
    crop = farm["crop_gu"]
    crop_en = farm.get("crop_en", crop)
    weather_en = weather.get("summary_en", weather["summary_gu"])
    weather_source_en = weather.get("source_label_en", weather["source_label"])
    price_crop_en = price.get("crop_en", price["crop_gu"])
    price_market_en = price.get("market_en", price["market_gu"])
    advisory_source_en = advisory.get("source_label_en", advisory["source_label"])
    as_of_en = advisory.get("as_of_en", advisory.get("as_of"))
    if intent == "greeting":
        return Answer("નમસ્તે! હું તમારા નમૂના ખેતરની માહિતી બતાવી શકું છું. હવામાન, પાણી, પાકની સ્થિતિ કે મંડીના નમૂના ભાવ વિશે પૂછો.", intent, follow_up="આજે ખેતરમાં શું જાણવું છે?", text_en="Hello! I can help with this sample farm. Ask about field status, irrigation, sample weather or a sample market price.", follow_up_en="What would you like to check today?")
    if intent == "status":
        return Answer(f"આ નમૂના {crop}ના ખેતરમાં પાક {farm['stage_gu']}માં છે. {advisory['advice_gu']} {advisory['reason_gu']} આ ખેતર અને માર્ગદર્શન કલ્પિત ડેમો છે.", intent, [farm["name_gu"], farm["stage_gu"], advisory["advice_gu"]], advisory["source_label"], advisory["as_of"], follow_up="છેલ્લે ખેતરમાં પાણી ક્યારે આપ્યું હતું?", text_en=f"In this sample {crop_en} field, the crop is at {farm.get('stage_en', farm['stage_gu'])}. {advisory.get('advice_en', advisory['advice_gu'])} {advisory.get('reason_en', advisory['reason_gu'])} This field and guidance are illustrative demo data.", follow_up_en="When was the field last irrigated?")
    if intent == "irrigation":
        return Answer(f"આ ડેમો {crop} ખેતર માટે પાણી આપતા પહેલાં માટીની ભેજ અને ખેતરની હાલત તપાસો. હવામાન સંકેત નમૂનાનો છે; અહીં માટીની ભેજ માપવામાં આવી નથી. {farm['last_irrigation_gu']} છેલ્લું પાણી આપ્યાનો કલ્પિત રેકોર્ડ છે.", intent, [weather["summary_gu"], farm["last_irrigation_gu"]], weather["source_label"], weather["as_of"], follow_up="માટી ઉપરથી સૂકી લાગે છે કે ભીની?", text_en=f"For this demo {crop_en} field, check the soil and field condition before irrigating. The weather cue is fictional; soil moisture has not been measured. The last irrigation entry ({farm.get('last_irrigation_en', farm['last_irrigation_gu'])}) is also sample data.", follow_up_en="Does the soil look dry or moist at the surface?")
    if intent == "weather":
        return Answer(f"{weather['summary_gu']}. {weather['why_gu']}", intent, [weather["summary_gu"]], weather["source_label"], weather["as_of"], follow_up="આગાહી મુજબ ખેતરની તૈયારી વિશે પૂછશો?", text_en=f"{weather_en}. {weather.get('why_en', weather['why_gu'])}", follow_up_en="Would you like to discuss how to check the field before acting?")
    if intent == "prices":
        return Answer(f"{price['crop_gu']}નો નમૂના ભાવ ₹{price['price_rupees_per_quintal']:,} પ્રતિ ક્વિન્ટલ બતાવ્યો છે ({price['market_gu']}). આ કલ્પિત જૂનો રેકોર્ડ છે, આજનો બજારભાવ નથી અને વેચાણની ખાતરી આપતો નથી.", intent, [price["market_gu"], price["crop_gu"]], price["source_label"], price["as_of"], follow_up="વાસ્તવિક ભાવ માટે સ્થાનિક મંડીમાં ચકાસો.", text_en=f"The sample {price_crop_en} price is ₹{price['price_rupees_per_quintal']:,} per quintal ({price_market_en}). This is an invented historical demo record, not today's market price or a guarantee of what a farmer will receive.", follow_up_en="Check with the local market for a current price.")
    if intent == "field":
        return Answer(f"તમે {farm['name_gu']} પસંદ કર્યું છે: {farm['area_acres']} એકર, {farm['crop_gu']}, {farm['stage_gu']}. છેલ્લી ડેમો નોંધ: {farm['recent_activity_gu']}. નકશો માત્ર કલ્પિત આકાર છે; સીમા સર્વે કરેલી નથી.", intent, [farm["name_gu"], farm["stage_gu"], farm["recent_activity_gu"]], farm["source_label"], farm["observed_at"], follow_up="બીજું નમૂના ખેતર જોવા માંગો છો?", text_en=f"Selected {farm.get('name_en', farm['name_gu'])}: {farm['area_acres']} acres, {crop_en}, {farm.get('stage_en', farm['stage_gu'])}. Latest demo note: {farm.get('recent_activity_en', farm['recent_activity_gu'])}. The map is illustrative; this boundary has not been surveyed.", follow_up_en="Would you like to see the other sample field?")
    if intent == "alert":
        return Answer(f"{alert['title_gu']}. કારણ: {alert['reason_gu']}", intent, [alert["title_gu"]], alert["source_label"], alert["as_of"], follow_up="આ ચેતવણીને ખેતરની હાલત સાથે સરખાવો.", text_en=f"{alert.get('title_en', alert['title_gu'])}. Why: {alert.get('reason_en', alert['reason_gu'])}", follow_up_en="Compare this reminder with what you see in the field.")
    if intent == "photo":
        return Answer("ફોટામાં દેખાતું લક્ષણ એકલું રોગ નક્કી કરવા પૂરતું નથી. આખા છોડનો અને પાનની નીચેની બાજુનો સ્પષ્ટ ફોટો લો; વરસાદ, ફેલાવા અને પાકની અવસ્થા વિશે નોંધો. દવા અથવા માત્રા નક્કી કરતાં પહેલાં સ્થાનિક કૃષિ નિષ્ણાત/KVKની સલાહ લો.", intent, ["ફોટો આધારિત નિદાન કરવામાં આવતું નથી"], "સાવચેતી માર્ગદર્શન", None, "ઓછો", follow_up="આ લક્ષણ કેટલા છોડમાં દેખાય છે?", text_en="A single photo is not enough to identify a disease. Take a clear picture of the whole plant and the underside of the leaf, and note recent rain, spread, and crop stage. Ask a local agriculture expert or KVK before choosing any treatment.", follow_up_en="How many plants show this symptom?")
    if intent == "high_risk":
        return Answer("દવા કે ખાતરની માત્રા હું નક્કી કરી શકતો નથી. પાક, લક્ષણ અને સ્થાનિક નિયમો જાણી કૃષિ અધિકારી/KVK અથવા યોગ્ય નિષ્ણાત પાસેથી ખાતરી કરો. તાત્કાલિક નુકસાન હોય તો ફોટા અને પાકની વિગતો સાથે તેમની મદદ લો.", intent, ["નિષ્ણાત સમીક્ષા જરૂરી"], "સુરક્ષા માર્ગદર્શન", None, "ઓછો", follow_up="શું તમે પાક અને દેખાતું લક્ષણ જણાવશો જેથી નિષ્ણાતને આપવાની નોંધ તૈયાર કરી શકું?", text_en="I can't recommend pesticide or fertilizer doses. Share the crop, symptoms, and local conditions with an agriculture officer, KVK, or qualified agronomist before acting. If damage is urgent, ask them to review clear photos and field details.", follow_up_en="Would you like help preparing a short note for an expert?")
    if intent == "unclear":
        return Answer("તમારો સવાલ સ્પષ્ટ સમજાયો નથી. કયું ખેતર, પાક અથવા મુદ્દો છે તે એક વાક્યમાં કહેશો?", intent, [], "", None, "ઓછો", follow_up="ઉદાહરણ: આજે મારા ખેતરમાં શું કરવું?", text_en="I didn't understand the question clearly. Which field, crop, or topic do you mean?", follow_up_en="For example: What should I do in my field today?")
    return Answer("આ સવાલ માટે ડેમોમાં ચકાસેલી માહિતી નથી. હું પાકની સ્થિતિ, પાણી, નમૂના હવામાન, નમૂના મંડીભાવ, ખેતર નકશો અથવા ફોટા અંગે સાવચેતીપૂર્વક મદદ કરી શકું છું.", "unsupported", [], "", None, "ઓછો", follow_up="આમાંથી કઈ બાબત વિશે પૂછવું છે?", text_en="I don't have verified demo information for that question. I can help with field status, irrigation, sample weather and market prices, the illustrative field map, or careful photo guidance.", follow_up_en="Which of those would you like to ask about?")
