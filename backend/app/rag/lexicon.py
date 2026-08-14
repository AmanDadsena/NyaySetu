"""
Cross-lingual bridge for retrieval.

The corpus is written in English but questions arrive in eight languages. Dense
multilingual embeddings solve this properly and are used when available (see
`retriever.py`); this lexicon is the always-on fallback that needs no model,
no download and no GPU. On a deployment without sentence-transformers it is the
*only* thing standing between a Tamil speaker and an empty answer, so its
coverage is load-bearing rather than decorative.

It maps legal vocabulary in Indian languages onto the English terms the corpus
actually uses. Entries are organised to mirror the corpus: every passage topic
has at least one route into it from each script, because a concept the corpus
can answer but the lexicon cannot spell is invisible to a non-English speaker.

Two details matter more than the size of the table:

  * **Inflection.** Indian languages inflect heavily and the corpus cannot
    enumerate every form — Hindi alone turns अधिकार into अधिकारों, अधिकारी,
    अधिकारों की. `expand` therefore falls back to a longest-prefix match after
    an exact lookup misses, which catches case endings without needing a
    morphological analyser.
  * **Compounds.** मकानमालिक ("landlord") is written both solid and spaced.
    Prefix matching handles the solid form; the spaced form matches on मकान.

Note that Indian-language legal writing very often keeps acronyms in Latin
script (FIR, RTI, NALSA, POSH), so those already match without help.
"""

from __future__ import annotations

#: Term in an Indian language -> English terms it should also search for.
LEXICON: dict[str, tuple[str, ...]] = {}

#: Shortest key we will accept from a prefix match. Below this, unrelated words
#: collide — Hindi जम would otherwise pull in both जमानत (bail) and जमा
#: (deposit), which belong to different areas of law.
_MIN_PREFIX = 3


def _add(english: str, *terms: str) -> None:
    """Register several native-language spellings for one English concept."""
    for term in terms:
        key = term.lower()
        LEXICON[key] = tuple(sorted(set(LEXICON.get(key, ()) + tuple(english.split()))))


# ── Core legal actors and places ────────────────────────────────────────
_add("lawyer advocate", "वकील", "वकिल", "વકીલ", "வழக்கறிஞர்", "న్యాయవాది", "আইনজীবী", "উকিল", "ವಕೀಲ")
_add("court", "न्यायालय", "अदालत", "કોર્ટ", "અદાલત", "நீதிமன்றம்", "కోర్టు", "న్యాయస్థానం", "আদালত", "ন্যায়ালয়", "ನ್ಯಾಯಾಲಯ")
_add("high court", "उच्च", "ઉચ્ચ", "உயர்", "హైకోర్టు", "উচ্চ", "ಉಚ್ಚ")
_add("supreme court", "सर्वोच्च", "उच्चतम", "સર્વોચ્ચ", "உச்ச", "సుప్రీం", "সুপ্রিম", "ಸರ್ವೋಚ್ಚ")
_add("police", "पुलिस", "पोलीस", "પોલીસ", "காவல்", "போலீஸ்", "పోలీసు", "পুলিশ", "ಪೊಲೀಸ್")
_add("police station", "थाना", "थाने", "ठाणे", "પોલીસસ્ટેશન", "காவல்நிலையம்", "పోలీస్‌స్టేషన్", "থানা", "ಠಾಣೆ")
_add("judge", "न्यायाधीश", "ન્યાયાધીશ", "நீதிபதி", "న్యాయమూర్తి", "বিচারক", "ನ್ಯಾಯಾಧೀಶ")
_add("magistrate", "मजिस्ट्रेट", "મેજિસ્ટ્રેટ", "நீதித்துறை", "మేజిస్ట్రేట్", "ম্যাজিস্ট্রেট", "ಮ್ಯಾಜಿಸ್ಟ್ರೇಟ್")
_add("government", "सरकार", "શાસન", "સરકાર", "அரசு", "ప్రభుత్వం", "সরকার", "ಸರ್ಕಾರ")
_add("case suit petition", "मुकदमा", "मामला", "केस", "खटला", "કેસ", "વાદ", "வழக்கு", "కేసు", "মামলা", "ಪ್ರಕರಣ", "ಮೊಕದ್ದಮೆ")
_add("file filing apply application", "दायर", "आवेदन", "अर्ज", "અરજી", "தாக்கல்", "விண்ணப்ப", "దరఖాస్తు", "আবেদন", "দাখিল", "ಅರ್ಜಿ")
_add("notice", "नोटिस", "सूचना", "નોટિસ", "அறிவிப்பு", "నోటీసు", "নোটিশ", "ನೋಟಿಸ್")
# Lodging a complaint, kept apart from property registration. Several languages
# use one verb for both — Gujarati નોંધાવવી is "to lodge" and નોંધણી is
# "registration" — and without the more specific entry the longer word falls
# back to the shorter stem and a consumer question lands on conveyancing.
_add("file filing lodge complaint report", "दर्ज", "नोंदव", "નોંધાવ", "பதிவு",
     "నమోదు", "নথিভুক্ত", "ದಾಖಲಿಸ")
_add("appeal", "अपील", "अपिल", "અપીલ", "மேல்முறையீடு", "అప్పీలు", "আপিল", "ಮೇಲ್ಮನವಿ")
_add("free legal aid", "निःशुल्क", "मुफ्त", "मोफत", "મફત", "இலவச", "ఉచిత", "বিনামূল্যে", "ಉಚಿತ")
_add("legal aid lok adalat", "लोकअदालत", "लोक", "લોકઅદાલત", "லோக்", "లోక్", "লোক", "ಲೋಕ್")

# ── Rights and law ──────────────────────────────────────────────────────
_add("rights", "अधिकार", "हक", "हक्क", "અધિકાર", "હક", "உரிமை", "హక్కు", "అధికారం", "অধিকার", "ಹಕ್ಕು")
_add("law act", "कानून", "कायदा", "विधि", "કાયદો", "சட்டம்", "చట్టం", "আইন", "ಕಾನೂನು")
_add("section", "धारा", "कलम", "કલમ", "பிரிவு", "సెక్షన్", "ধারা", "ಸೆಕ್ಷನ್", "ಪರಿಚ್ಛೇದ")
_add("constitution fundamental rights", "संविधान", "બંધારણ", "அரசியலமைப்பு", "రాజ్యాంగం", "সংবিধান", "ಸಂವಿಧಾನ")
_add("article", "अनुच्छेद", "અનુચ્છેદ", "பிரிவு", "అధికరణ", "অনুচ্ছেদ", "ವಿಧಿ")
_add("equality equal", "समानता", "समान", "સમાનતા", "சமத்துவம்", "సమానత్వం", "সমতা", "ಸಮಾನತೆ")
_add("freedom speech expression", "स्वतंत्रता", "आजादी", "स्वातंत्र्य", "સ્વતંત્રતા", "சுதந்திரம்", "స్వేచ్ఛ", "স্বাধীনতা", "ಸ್ವಾತಂತ್ರ್ಯ")
_add("religion", "धर्म", "ધર્મ", "மதம்", "మతం", "ধর্ম", "ಧರ್ಮ")
_add("education school", "शिक्षा", "शिक्षण", "શિક્ષણ", "கல்வி", "విద్య", "শিক্ষা", "ಶಿಕ್ಷಣ")
_add("complaint", "शिकायत", "तक्रार", "ફરિયાદ", "புகார்", "ఫిర్యాదు", "অভিযোগ", "ದೂರು")
_add("writ habeas corpus", "याचिका", "રિટ", "மனு", "రిట్", "রিট", "ಅರ್ಜಿ")
_add("privacy data protection", "निजता", "गोपनीयता", "ગોપનીયતા", "தனியுரிமை", "గోప్యత", "গোপনীয়তা", "ಗೌಪ್ಯತೆ")
_add("duties", "कर्तव्य", "કર્તવ્ય", "கடமை", "కర్తవ్యం", "কর্তব্য", "ಕರ್ತವ್ಯ")

# ── Criminal ────────────────────────────────────────────────────────────
_add("arrest arrested", "गिरफ्तार", "गिरफ्तारी", "अटक", "ધરપકડ", "கைது", "అరెస్టు", "গ্রেপ্তার", "ಬಂಧನ", "ಬಂಧ")
_add("bail", "जमानत", "जामीन", "જામીન", "பிணை", "బెయిల్", "জামিন", "ಜಾಮೀನು")
_add("anticipatory bail", "अग्रिम", "अटकपूर्व", "આગોતરા", "முன்ஜாமீன்", "ముందస్తు", "আগাম", "ನಿರೀಕ್ಷಣಾ")
_add("fir police complaint", "प्राथमिकी", "एफआईआर", "एफआयआर", "એફઆઈઆર", "எஃப்ஐஆர்", "ఎఫ్ఐఆర్", "এফআইআর", "ಎಫ್ಐಆರ್")
_add("custody detention", "हिरासत", "कोठडी", "અટકાયત", "காவலில்", "కస్టడీ", "হেফাজত", "ಕಸ್ಟಡಿ")
_add("crime offence", "अपराध", "गुन्हा", "ગુનો", "குற்றம்", "నేరం", "অপরাধ", "ಅಪರಾಧ")
_add("accused", "आरोपी", "आरोप", "આરોપી", "குற்றவாளி", "నిందితుడు", "অভিযুক্ত", "ಆರೋಪಿ")
_add("murder", "हत्या", "खून", "હત્યા", "கொலை", "హత్య", "খুন", "ಕೊಲೆ")
_add("theft snatching steal", "चोरी", "ચોરી", "திருட்டு", "దొంగతనం", "চুরি", "ಕಳ್ಳತನ")
_add("assault hurt beating", "मारपीट", "हमला", "મારપીટ", "தாக்குதல்", "దాడి", "মারধর", "ಹಲ್ಲೆ")
_add("threat extortion", "धमकी", "ધમકી", "மிரட்டல்", "బెదిరింపు", "হুমকি", "ಬೆದರಿಕೆ")
_add("evidence witness", "साक्ष्य", "सबूत", "गवाह", "પુરાવો", "சாட்சி", "సాక్ష్యం", "সাক্ষী", "ಸಾಕ್ಷ್ಯ")
_add("sedition", "राजद्रोह", "देशद्रोह", "રાજદ્રોહ", "தேசத்துரோகம்", "రాజద్రోహం", "রাষ্ট্রদ্রোহ", "ದೇಶದ್ರೋಹ")
_add("mob lynching", "भीड", "लिंचिंग", "ટોળા", "கும்பல்", "గుంపు", "গণপিটুনি", "ಗುಂಪು")
_add("stalking", "पीछा", "પીછો", "தொடர்ந்து", "వెంబడించ", "অনুসরণ", "ಹಿಂಬಾಲಿ")
_add("defamation", "मानहानि", "बदनामी", "માનહાનિ", "அவதூறு", "పరువునష్టం", "মানহানি", "ಮಾನಹಾನಿ")
_add("negligence hit and run", "लापरवाही", "निष्काळजी", "બેદરકારી", "கவனக்குறைவு", "నిర్లక్ష్యం", "অবহেলা", "ನಿರ್ಲಕ್ಷ್ಯ")

# ── Family ──────────────────────────────────────────────────────────────
_add("divorce", "तलाक", "घटस्फोट", "છૂટાછેડા", "விவாகரத்து", "విడాకులు", "বিবাহবিচ্ছেদ", "ವಿಚ್ಛೇದನ")
_add("mutual consent", "आपसी", "सहमति", "પરસ્પર", "பரஸ்பர", "పరస్పర", "পারস্পরিক", "ಪರಸ್ಪರ")
_add("marriage", "विवाह", "शादी", "लग्न", "લગ્ન", "திருமணம்", "వివాహం", "বিবাহ", "ಮದುವೆ")
_add("maintenance alimony", "भरण", "पोषण", "गुजारा", "ભરણપોષણ", "ஜீவனாம்சம்", "భరణం", "ভরণপোষণ", "ಜೀವನಾಂಶ")
_add("domestic violence", "घरेलू", "कौटुंबिक", "ઘરેલું", "குடும்ப", "గృహ", "গার্হস্থ্য", "ಕೌಟುಂಬಿಕ")
_add("cruelty husband", "क्रूरता", "पति", "ક્રૂરતા", "கொடுமை", "క్రూరత్వం", "নিষ্ঠুরতা", "ಕ್ರೌರ್ಯ")
_add("dowry", "दहेज", "हुंडा", "દહેજ", "வரதட்சணை", "కట్నం", "যৌতুক", "ವರದಕ್ಷಿಣೆ")
_add("wife woman women", "पत्नी", "महिला", "स्त्री", "बायको", "પત્ની", "મહિલા", "மனைவி", "பெண்", "భార్య", "మహిళ", "স্ত্রী", "মহিলা", "ಪತ್ನಿ", "ಮಹಿಳೆ")
_add("child children", "बच्चा", "बच्चों", "बालक", "મુલ", "બાળક", "குழந்தை", "పిల్లలు", "শিশু", "ಮಗು", "ಮಕ್ಕಳು")
_add("parents senior citizens", "माता", "पिता", "आईवडील", "बुजुर्ग", "માતાપિતા", "பெற்றோர்", "తల్లిదండ్రులు", "পিতামাতা", "ಪೋಷಕರು", "ಹಿರಿಯ")
_add("custody guardianship", "अभिरक्षा", "संरक्षक", "કસ્ટડી", "பாதுகாப்பு", "సంరక్షణ", "অভিভাবক", "ಪಾಲನೆ")

# ── Property and money ──────────────────────────────────────────────────
_add("property land", "संपत्ति", "जमीन", "मालमत्ता", "जायदाद", "મિલકત", "જમીન", "சொத்து", "ఆస్తి", "সম্পত্তি", "ಆಸ್ತಿ")
_add("inheritance succession daughter", "उत्तराधिकार", "वारसा", "विरासत", "વારસો", "வாரிசு", "వారసత్వం", "উত্তরাধিকার", "ಉತ್ತರಾಧಿಕಾರ")
_add("ancestral coparcenary property", "पैतृक", "पितृ", "वडिलोपार्जित", "પૈતૃક", "વડીલોપાર્જિત",
     "மூதாதையர்", "పూర్వీకుల", "পৈতৃক", "ಪಿತ್ರಾರ್ಜಿತ")
_add("daughter daughters coparcenary", "बेटी", "पुत्री", "मुलगी", "मुली", "દીકરી", "પુત્રી",
     "மகள்", "కుమార్తె", "కూతురు", "মেয়ে", "কন্যা", "ಮಗಳು", "ಪುತ್ರಿ")
_add("son", "बेटा", "पुत्र", "मुलगा", "દીકરો", "மகன்", "కుమారుడు", "ছেলে", "ಮಗ")
_add("will testament", "वसीयत", "मृत्युपत्र", "વસિયત", "உயில்", "వీలునామా", "উইল", "ಉಯಿಲು")
_add("registration registry stamp duty", "पंजीकरण", "रजिस्ट्री", "નોંધણી", "பதிவு", "నమోదు", "নিবন্ধন", "ನೋಂದಣಿ")
_add("rent tenant landlord", "किराया", "किरायेदार", "भाड", "भाडेकरू", "ભાડું", "ભાડુઆત", "வாடகை", "குத்தகை", "అద్దె", "ভাড়া", "ಬಾಡಿಗೆ")
# House and landlord are the words people actually reach for in a deposit
# dispute. Without them "return my deposit" expands only to refund vocabulary
# and lands on the e-commerce passage instead of the tenancy one.
_add("house home landlord tenant rent", "मकान", "घर", "मकानमालिक", "घरमालिक", "घरमालक",
     "મકાન", "ઘર", "મકાનમાલિક", "வீடு", "வீட்டு", "இல்லம்",
     "ఇల్లు", "ఇంటి", "యజమాని", "বাড়ি", "বাড়িওয়ালা", "ಮನೆ", "ಮಾಲೀಕ")
_add("deposit security tenant", "जमा", "अनामत", "ठेव", "ડિપોઝિટ", "થાપણ", "வைப்பு", "డిపాజిట్", "জমা", "ಠೇವಣಿ")
_add("eviction vacate", "बेदखल", "खाली", "કાઢી", "வெளியேற்ற", "ఖాళీ", "উচ্ছেদ", "ತೆರವು")
_add("refund return money", "वापसी", "लौटा", "परत", "રિફંડ", "પરત", "திரும்ப", "వాపసు", "ফেরত", "ಮರುಪಾವತಿ", "ಹಿಂತಿರುಗಿ")
_add("money amount payment rupees", "पैसा", "रकम", "राशि", "रुपये", "પૈસા", "રકમ", "பணம்", "தொகை", "డబ్బు", "మొత్తం", "টাকা", "পরিমাণ", "ಹಣ", "ಮೊತ್ತ")
_add("cheque bounce", "चेक", "ચેક", "காசோலை", "చెక్", "চেক", "ಚೆಕ್")
_add("bank account fraud", "बैंक", "खाता", "બેંક", "வங்கி", "బ్యాంకు", "ব্যাংক", "ಬ್ಯಾಂಕ್")
_add("loan debt recovery", "कर्ज", "ऋण", "उधार", "લોન", "કરજ", "கடன்", "అప్పు", "ঋণ", "ಸಾಲ")
_add("consumer refund", "उपभोक्ता", "ग्राहक", "ગ્રાહક", "நுகர்வோர்", "వినియోగదారు", "ভোক্তা", "ক্রেতা", "ಗ್ರಾಹಕ")
_add("insurance claim", "बीमा", "વીમો", "காப்பீடு", "బీమా", "বীমা", "ವಿಮೆ")
_add("contract agreement", "अनुबंध", "करार", "समझौता", "કરાર", "ஒப்பந்தம்", "ఒప్పందం", "চুক্তি", "ಒಪ್ಪಂದ")

# ── Work ────────────────────────────────────────────────────────────────
_add("employment job worker employer", "नौकरी", "कर्मचारी", "मालिक", "नोकरी", "નોકરી", "કર્મચારી", "வேலை", "ஊழியர்", "ఉద్యోగం", "చాకిరి", "চাকরি", "কর্মচারী", "ಉದ್ಯೋಗ", "ನೌಕರ")
_add("wages salary unpaid", "वेतन", "मजदूरी", "तनख्वाह", "पगार", "પગાર", "ઊતરી", "ஊதியம்", "சம்பளம்", "వేతనం", "జీతం", "মজুরি", "বেতন", "ವೇತನ", "ಸಂಬಳ")
_add("maternity leave", "मातृत्व", "प्रसूति", "પ્રસૂતિ", "மகப்பேறு", "ప్రసూతి", "মাতৃত্ব", "ಹೆರಿಗೆ")
_add("gratuity", "ग्रेच्युटी", "ગ્રેચ્યુઇટી", "பணிக்கொடை", "గ్రాట్యుటీ", "গ্র্যাচুইটি", "ಗ್ರಾಚುಟಿ")
_add("terminate dismissal fired", "बर्खास्त", "निकाल", "बडतर्फ", "બરતરફ", "பணிநீக்கம்", "తొలగింపు", "বরখাস্ত", "ವಜಾ")
_add("harassment", "उत्पीड़न", "छळ", "उत्पीडन", "સતામણી", "துன்புறுத்தல்", "వేధింపు", "হয়রানি", "ಕಿರುಕುಳ")
_add("workplace office", "कार्यस्थल", "कार्यालय", "કાર્યસ્થળ", "பணியிடம்", "కార్యాలయం", "কর্মক্ষেত্র", "ಕೆಲಸದ")

# ── Everyday / welfare ──────────────────────────────────────────────────
_add("cyber crime online fraud", "साइबर", "ऑनलाइन", "સાયબર", "சைபர்", "సైబర్", "সাইবার", "ಸೈಬರ್")
_add("fraud cheating", "धोखा", "ठगी", "फसवणूक", "છેતરપિંડી", "மோசடி", "మోసం", "প্রতারণা", "ವಂಚನೆ")
_add("information rti", "सूचना", "जानकारी", "माहिती", "માહિતી", "தகவல்", "సమాచారం", "তথ্য", "ಮಾಹಿತಿ")
_add("ration food security", "राशन", "રેશન", "ரேஷன்", "రేషన్", "রেশন", "ರೇಷನ್")
_add("traffic challan driving licence", "यातायात", "चालान", "वाहतूक", "लाइसेंस", "ડ્રાઇવિંગ", "ટ્રાફિક", "போக்குவரத்து", "உரிமம்", "ట్రాఫిక్", "లైసెన్స్", "ট্রাফিক", "লাইসেন্স", "ಸಂಚಾರ", "ಚಾಲನಾ")
_add("vehicle car bike", "वाहन", "गाड़ी", "વાહન", "வாகனம்", "వాహనం", "যানবাহন", "ವಾಹನ")
_add("accident compensation", "दुर्घटना", "मुआवजा", "अपघात", "અકસ્માત", "વળતર", "விபத்து", "இழப்பீடு", "ప్రమాదం", "పరిహారం", "দুর্ঘটনা", "ক্ষতিপূরণ", "ಅಪಘಾತ", "ಪರಿಹಾರ")
_add("caste atrocity", "जाति", "जात", "अत्याचार", "જાતિ", "சாதி", "కులం", "জাতি", "ಜಾತಿ")
_add("disability disabled", "विकलांग", "दिव्यांग", "અપંગ", "மாற்றுத்திறனாளி", "వికలాంగ", "প্রতিবন্ধী", "ಅಂಗವಿಕಲ")
_add("mental health illness", "मानसिक", "માનસિક", "மனநல", "మానసిక", "মানসিক", "ಮಾನಸಿಕ")
_add("passport", "पासपोर्ट", "પાસપોર્ટ", "கடவுச்சீட்டு", "పాస్‌పోర్ట్", "পাসপোর্ট", "ಪಾಸ್‌ಪೋರ್ಟ್")
_add("noise pollution loudspeaker", "शोर", "ध्वनि", "અવાજ", "ஒலி", "శబ్ద", "শব্দ", "ಶಬ್ದ")
_add("missing person", "लापता", "गुमशुदा", "ગુમ", "காணாமல்", "తప్పిపోయిన", "নিখোঁজ", "ಕಾಣೆ")
_add("time limit limitation", "समयसीमा", "अवधि", "मुदत", "સમયમર્યાદા", "காலவரம்பு", "గడువు", "সময়সীমা", "ಕಾಲಮಿತಿ")


def _register_stems() -> None:
    """
    Register shortened forms of each key so inflection cannot hide a match.

    Prefix matching alone only helps when the key is a prefix of the word the
    user typed. Real inflection often diverges before that: Telugu విడాకులు
    ("divorce") becomes విడాకులకు in the dative, and the two part company at the
    seventh character, so neither is a prefix of the other. Trimming the key
    back to విడాకుల gives both a common landing point.

    An alias is dropped when two keys with *different* meanings produce it, so
    shortening never silently merges unrelated concepts — better to miss than to
    answer a bail question with tenancy law.
    """
    candidates: dict[str, set[tuple[str, ...]]] = {}
    for key, terms in LEXICON.items():
        if key.isascii():
            continue
        for cut in (1, 2):
            stem = key[:-cut]
            if len(stem) < _MIN_PREFIX or stem in LEXICON:
                continue
            candidates.setdefault(stem, set()).add(terms)

    for stem, meanings in candidates.items():
        if len(meanings) == 1:
            LEXICON[stem] = next(iter(meanings))


_register_stems()


def _lookup(token: str) -> tuple[str, ...] | None:
    """
    Find the English terms for one native-language token.

    Exact match first. Failing that — and only for non-Latin scripts, where
    English suffix stemming does not apply — the longest prefix of the token
    that is a known key wins, which is what lets अधिकारों reach अधिकार and
    मकानमालिक reach मकान without enumerating every inflected form.
    """
    hit = LEXICON.get(token)
    if hit is not None:
        return hit
    if token.isascii():
        return None
    for end in range(len(token) - 1, _MIN_PREFIX - 1, -1):
        hit = LEXICON.get(token[:end])
        if hit is not None:
            return hit
    return None


def expand(tokens: list[str]) -> list[str]:
    """Append English equivalents for any recognised non-English tokens."""
    extra: list[str] = []
    for token in tokens:
        mapped = _lookup(token)
        if mapped:
            extra.extend(mapped)
    return tokens + extra
