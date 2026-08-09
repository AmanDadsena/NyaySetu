"""
Cross-lingual bridge for retrieval.

The corpus is written in English but questions arrive in eight languages. Dense
multilingual embeddings solve this properly and are used when available (see
`retriever.py`); this lexicon is the always-on fallback that needs no model,
no download and no GPU.

It maps legal vocabulary in Indian languages onto the English terms the corpus
actually uses. Coverage is deliberately concentrated on the concepts people
actually ask about — arrest, FIR, divorce, maintenance, property, ration —
rather than attempting a general dictionary.

Note that Indian-language legal writing very often keeps acronyms in Latin
script (FIR, RTI, NALSA, POSH), so those already match without help.
"""

from __future__ import annotations

#: Term in an Indian language -> English terms it should also search for.
LEXICON: dict[str, tuple[str, ...]] = {}


def _add(english: str, *terms: str) -> None:
    """Register several native-language spellings for one English concept."""
    for term in terms:
        LEXICON.setdefault(term.lower(), ())
        LEXICON[term.lower()] = tuple(set(LEXICON[term.lower()] + tuple(english.split())))


# ── Core legal actors and places ────────────────────────────────────────
_add("lawyer advocate", "वकील", "वकीलांना", "વકીલ", "வழக்கறிஞர்", "న్యాయవాది", "আইনজীবী", "ವಕೀಲ")
_add("court", "न्यायालय", "अदालत", "કોર્ટ", "અદાલત", "நீதிமன்றம்", "కోర్టు", "న్యాయస్థానం", "আদালত", "ন্যায়ালয়", "ನ್ಯಾಯಾಲಯ")
_add("police", "पुलिस", "पोलीस", "પોલીસ", "காவல்", "போலீஸ்", "పోలీసు", "পুলিশ", "ಪೊಲೀಸ್")
_add("judge", "न्यायाधीश", "न्यायाधीश", "ન્યાયાધીશ", "நீதிபதி", "న్యాయమూర్తి", "বিচারক", "ನ್ಯಾಯಾಧೀಶ")
_add("government", "सरकार", "સરકાર", "அரசு", "ప్రభుత్వం", "সরকার", "ಸರ್ಕಾರ")

# ── Rights and law ──────────────────────────────────────────────────────
_add("rights", "अधिकार", "हक्क", "અધિકાર", "உரிமை", "உரிமைகள்", "హక్కులు", "అధికారం", "অধিকার", "ಹಕ್ಕು", "ಹಕ್ಕುಗಳು")
_add("law act", "कानून", "कायदा", "કાયદો", "சட்டம்", "చట్టం", "আইন", "ಕಾನೂನು")
_add("constitution fundamental rights", "संविधान", "બંધારણ", "அரசியலமைப்பு", "రాజ్యాంగం", "সংবিধান", "ಸಂವಿಧಾನ")
_add("free legal aid", "निःशुल्क", "मुफ्त", "मोफत", "મફત", "இலவச", "ఉచిత", "বিনামূল্যে", "ಉಚಿತ")
_add("complaint", "शिकायत", "तक्रार", "ફરિયાદ", "புகார்", "ఫిర్యాదు", "অভিযোগ", "ದೂರು")

# ── Criminal ────────────────────────────────────────────────────────────
_add("arrest arrested", "गिरफ्तार", "गिरफ्तारी", "अटक", "ધરપકડ", "கைது", "అరెస్టు", "গ্রেপ্তার", "ಬಂಧನ")
_add("bail", "जमानत", "जामीन", "જામીન", "பிணை", "బెయిల్", "জামিন", "ಜಾಮೀನು")
_add("fir police complaint", "प्राथमिकी", "एफआईआर", "एफआयआर", "એફઆઈઆર", "எஃப்ஐஆர்", "ఎఫ్ఐఆర్", "এফআইআর", "ಎಫ್ಐಆರ್")
_add("custody detention", "हिरासत", "कोठडी", "અટકાયત", "காவல்", "కస్టడీ", "হেফাজত", "ಕಸ್ಟಡಿ")
_add("crime offence", "अपराध", "गुन्हा", "ગુનો", "குற்றம்", "నేరం", "অপরাধ", "ಅಪರಾಧ")
_add("murder", "हत्या", "खून", "હત્યા", "கொலை", "హత్య", "খুন", "ಕೊಲೆ")
_add("theft snatching", "चोरी", "ચોરી", "திருட்டு", "దొంగతనం", "চুরি", "ಕಳ್ಳತನ")

# ── Family ──────────────────────────────────────────────────────────────
_add("divorce", "तलाक", "घटस्फोट", "છૂટાછેડા", "விவாகரத்து", "విడాకులు", "বিবাহবিচ্ছেদ", "ವಿಚ್ಛೇದನ")
_add("marriage", "विवाह", "शादी", "लग्न", "લગ્ન", "திருமணம்", "వివాహం", "বিবাহ", "ಮದುವೆ")
_add("maintenance alimony", "भरण", "पोषण", "गुजारा", "ભરણપોષણ", "ஜீவனாம்சம்", "భరణం", "ভরণপোষণ", "ಜೀವನಾಂಶ")
_add("domestic violence", "घरेलू", "कौटुंबिक", "ઘરેલું", "குடும்ப", "గృహ", "গার্হস্থ্য", "ಕೌಟುಂಬಿಕ")
_add("dowry", "दहेज", "हुंडा", "દહેજ", "வரதட்சணை", "కట్నం", "যৌতুক", "ವರದಕ್ಷಿಣೆ")
_add("wife woman women", "पत्नी", "महिला", "स्त्री", "પત્ની", "મહિલા", "மனைவி", "பெண்", "భార్య", "మహిళ", "স্ত্রী", "মহিলা", "ಪತ್ನಿ", "ಮಹಿಳೆ")
_add("child children", "बच्चा", "बच्चों", "मुल", "બાળક", "குழந்தை", "పిల్లలు", "শিশু", "ಮಗು", "ಮಕ್ಕಳು")
_add("parents senior citizens", "माता", "पिता", "आईवडील", "માતાપિતા", "பெற்றோர்", "తల్లిదండ్రులు", "পিতামাতা", "ಪೋಷಕರು")

# ── Property and money ──────────────────────────────────────────────────
_add("property land", "संपत्ति", "जमीन", "मालमत्ता", "મિલકત", "சொத்து", "ఆస్తి", "সম্পত্তি", "ಆಸ್ತಿ")
_add("inheritance succession daughter", "उत्तराधिकार", "वारसा", "વારસો", "வாரிசு", "వారసత్వం", "উত্তরাধিকার", "ಉತ್ತರಾಧಿಕಾರ")
_add("rent tenant landlord", "किराया", "भाड", "ભાડું", "வாடகை", "అద్దె", "ভাড়া", "ಬಾಡಿಗೆ")
_add("cheque bounce", "चेक", "ચેક", "காசோலை", "చెక్", "চেক", "ಚೆಕ್")
_add("consumer refund", "उपभोक्ता", "ग्राहक", "ગ્રાહક", "நுகர்வோர்", "వినియోగదారు", "ভোক্তা", "ಗ್ರಾಹಕ")

# ── Work ────────────────────────────────────────────────────────────────
_add("employment job worker", "नौकरी", "कर्मचारी", "नोकरी", "નોકરી", "வேலை", "ఉద్యోగం", "চাকরি", "ಉದ್ಯೋಗ")
_add("wages salary", "वेतन", "मजदूरी", "પગાર", "ஊதியம்", "వేతనం", "মজুরি", "ವೇತನ")
_add("maternity leave", "मातृत्व", "પ્રસૂતિ", "மகப்பேறு", "ప్రసూతి", "মাতৃত্ব", "ಹೆರಿಗೆ")
_add("gratuity", "ग्रेच्युटी", "ગ્રેચ્યુઇટી", "பணிக்கொடை", "గ్రాట్యుటీ", "গ্র্যাচুইটি", "ಗ್ರಾಚುಟಿ")

# ── Everyday / welfare ──────────────────────────────────────────────────
_add("cyber crime online fraud", "साइबर", "સાયબર", "சைபர்", "సైబర్", "সাইবার", "ಸೈಬರ್")
_add("fraud cheating", "धोखा", "ठगी", "फसवणूक", "છેતરપિંડી", "மோசடி", "మోసం", "প্রতারণা", "ವಂಚನೆ")
_add("information rti", "सूचना", "जानकारी", "माहिती", "માહિતી", "தகவல்", "సమాచారం", "তথ্য", "ಮಾಹಿತಿ")
_add("ration food security", "राशन", "રેશન", "ரேஷன்", "రేషన్", "রেশন", "ರೇಷನ್")
_add("traffic challan driving", "यातायात", "वाहतूक", "ટ્રાફિક", "போக்குவரத்து", "ట్రాఫిక్", "ট্রাফিক", "ಸಂಚಾರ")
_add("harassment", "उत्पीड़न", "छळ", "સતામણી", "துன்புறுத்தல்", "వేధింపు", "হয়রানি", "ಕಿರುಕುಳ")
_add("caste", "जाति", "जात", "જાતિ", "சாதி", "కులం", "জাতি", "ಜಾತಿ")


def expand(tokens: list[str]) -> list[str]:
    """Append English equivalents for any recognised non-English tokens."""
    extra: list[str] = []
    for token in tokens:
        mapped = LEXICON.get(token)
        if mapped:
            extra.extend(mapped)
    return tokens + extra
