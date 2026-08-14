"""
Retrieval evaluation.

This is the part of "training" that is actually defensible for this system.
There is no fine-tune to measure, but there *is* a retriever, and a retriever
can be scored: given a question a real user might ask, does the correct statute
come back, and does it come back first?

Run it:

    python -m app.rag.eval

Every question below names the passage that should be retrieved. Two metrics
are reported — hit@3 (is the right passage anywhere in the top three) and MRR
(how high it ranked). Both are standard for retrieval work, so the numbers mean
something to a reviewer.

Add a case whenever you add a passage. A corpus change that improves one topic
and quietly breaks another is otherwise invisible.
"""

from __future__ import annotations

import sys
import unicodedata

from .lexicon import LEXICON
from .retriever import get_retriever

#: Scripts the lexicon is written in. Devanagari covers both Hindi and Marathi.
_SCRIPTS = ("DEVANAGARI", "GUJARATI", "TAMIL", "TELUGU", "BENGALI", "KANNADA")


#: Danda and double danda. They sit in the Devanagari block but are shared
#: sentence punctuation across Indic scripts — Bengali, Gujarati and the rest
#: all use them — so they say nothing about which script a string is written in.
#: Counting them flagged the Bengali refusal as containing Devanagari.
_SHARED_PUNCTUATION = {"।", "॥"}


def _scripts_in(term: str) -> set[str]:
    found = set()
    for char in term:
        if char in _SHARED_PUNCTUATION:
            continue
        try:
            name = unicodedata.name(char)
        except ValueError:
            continue
        for script in _SCRIPTS:
            if name.startswith(script):
                found.add(script)
    return found


#: Which script each UI language must be written in.
_EXPECTED_SCRIPT = {
    "Hindi": "DEVANAGARI", "Marathi": "DEVANAGARI", "Gujarati": "GUJARATI",
    "Tamil": "TAMIL", "Telugu": "TELUGU", "Bengali": "BENGALI",
    "Kannada": "KANNADA",
}


def check_translations() -> list[str]:
    """
    Catch the same hand-written script mixing in the user-facing strings.

    The lexicon check below covers retrieval terms. This covers the refusal
    message, which is the one reply a user sees when nothing matched — and the
    only one written by hand in eight languages rather than produced by a model.
    A Devanagari consonant inside a Tamil sentence renders as a stray glyph and
    was shipped exactly that way once.
    """
    from .engine import _NO_MATCH

    problems = []
    for language, text in _NO_MATCH.items():
        expected = _EXPECTED_SCRIPT.get(language)
        if expected is None:  # English, or a language with no script to check
            continue
        found = _scripts_in(text) - {expected}
        if found:
            problems.append(f"{language} refusal contains {sorted(found)}")
        if not _scripts_in(text):
            problems.append(f"{language} refusal has no {expected} characters at all")

    missing = sorted(set(_EXPECTED_SCRIPT) - set(_NO_MATCH))
    if missing:
        problems.append(f"no localised refusal for {missing} — they fall back to English")
    return problems


def check_lexicon() -> list[str]:
    """
    Catch entries that are not really words in the language they claim.

    A term assembled from two scripts — a Tamil stem carrying a Telugu vowel
    sign, say — looks plausible in a diff and matches nothing at all, because
    no keyboard in either language produces it. Three such entries were written
    by hand and shipped before this check existed. A Latin-letter key is the
    other failure mode: it silently shadows an English token.
    """
    problems = []
    for key in LEXICON:
        scripts = _scripts_in(key)
        if len(scripts) > 1:
            problems.append(f"{key!r} mixes {sorted(scripts)}")
        if any("a" <= c <= "z" for c in key):
            problems.append(f"{key!r} contains Latin letters")
    return problems

#: (question, id of the passage that should be retrieved)
CASES: list[tuple[str, str]] = [
    # Police and criminal procedure
    ("What are my rights if the police arrest me?", "arrest_rights"),
    ("Police are refusing to file my FIR, what do I do?", "fir_refusal_remedy"),
    ("How do I register a first information report?", "fir_how_to_file"),
    ("The police say the crime happened in another area", "zero_fir"),
    ("Can I get bail before being arrested?", "anticipatory_bail"),
    ("Police have not filed a charge sheet in 90 days", "bail_default"),
    ("How do I complain about a police officer?", "police_complaint_against"),
    ("My child is missing, will police wait 24 hours?", "missing_person"),

    # Access to justice
    ("I cannot afford a lawyer, is there free legal help?", "legal_aid_eligibility"),
    ("Where do I apply for free legal aid?", "legal_aid_how_to_apply"),
    ("Can I settle my case without a full trial?", "lok_adalat"),

    # Constitution
    ("What are the fundamental rights in the Constitution?", "fundamental_rights"),
    ("What does the right to life cover?", "article_21"),
    ("How do I file a writ petition for habeas corpus?", "article_32"),
    ("Can Parliament amend any part of the Constitution?", "kesavananda"),
    ("Is privacy a fundamental right in India?", "puttaswamy"),
    ("What are the limits on freedom of speech?", "article_19_freedoms"),
    ("Is my child entitled to free schooling?", "article_21a_education"),
    ("What are the directive principles of state policy?", "directive_principles"),

    # Traffic
    ("What is the fine for drunk driving?", "mv_penalties_core"),
    ("How do I check and pay my e-challan?", "echallan_dispute"),
    ("What documents must I carry while driving?", "mv_documents_required"),
    ("How do I apply for a driving licence?", "mv_licence_how_to"),
    ("My son who is 16 was caught driving my car", "mv_juvenile_offence"),
    ("How do I claim compensation after a road accident?", "accident_compensation"),
    ("I sold my bike, do I need to transfer the RC?", "vehicle_transfer"),

    # Consumer and money
    ("Where do I file a consumer complaint?", "consumer_where_to_file"),
    ("An online seller refuses to refund me", "e_commerce_rights"),
    ("Money was taken from my bank account by fraud", "banking_fraud_liability"),
    ("My insurance claim was rejected", "insurance_claim_rejected"),
    ("Someone gave me a cheque that bounced", "cheque_bounce"),

    # Family and property
    ("What are the grounds for divorce?", "divorce_grounds_hindu"),
    ("We both want a divorce by mutual consent", "divorce_mutual_consent"),
    ("Can I claim maintenance from my husband?", "maintenance"),
    ("My husband is violent, what protection is there?", "domestic_violence"),
    ("Does a daughter have rights in ancestral property?", "daughters_coparcenary"),
    ("How do I claim my late father's bank balance?", "succession_certificate"),
    ("My son refuses to look after me, I gave him my house", "senior_citizens_maintenance"),

    # Work
    ("My employer has not paid my salary", "wage_theft"),
    ("Am I entitled to gratuity after five years?", "gratuity"),
    ("How much maternity leave am I entitled to?", "maternity_benefit"),
    ("Is my non-compete clause enforceable after I resign?", "contract_restraint"),
    ("I was harassed at work by my manager", "vishaka_posh"),

    # Cyber, data, other
    ("I was cheated in an online scam", "cybercrime_reporting"),
    ("Someone posted my private photos online", "obscene_content_online"),
    ("A man keeps following and messaging me", "bns_stalking"),
    ("What rights do I have over my personal data?", "data_protection"),
    ("How do I file an RTI application?", "rti_how_to_file"),
    ("My RTI was refused, can I appeal?", "rti_appeals"),
    ("My neighbours play loudspeakers at midnight", "noise_pollution"),
    ("What replaced the Indian Penal Code?", "bns_overview"),
    ("How long do I have to file a civil suit?", "limitation_periods"),
    ("Someone is spreading lies about me publicly", "defamation"),
    ("I have a disability, what reservation applies?", "disability_rights"),
    ("Am I entitled to subsidised ration?", "ration_food_security"),

    # Civil procedure
    ("Should I send a legal notice before suing?", "legal_notice_before_suit"),
    ("What goes into a plaint when starting a civil case?", "civil_suit_how_to_file"),
    ("I cannot pay the court fee, can it be waived?", "court_fees_basics"),
    ("My contract says disputes go to arbitration", "arbitration_basics"),
    ("Is mediation compulsory before a commercial suit?", "mediation_pre_litigation"),
    ("I need a stay order to stop them demolishing my wall", "injunction_stay"),

    # Housing and land
    ("The builder has not given possession of my flat", "rera_homebuyer"),
    ("How do I get the revenue record changed to my name?", "property_mutation"),
    ("How do I check if a property has a loan on it?", "encumbrance_certificate"),
    ("My brothers will not divide our father's land", "partition_property"),
    ("Can a gift deed be cancelled later?", "gift_deed"),
    ("Is my rent agreement a lease or a licence?", "lease_vs_licence"),
    ("The government is acquiring my land, what compensation?", "land_acquisition_compensation"),
    ("The society cut my water over unpaid maintenance", "housing_society_dispute"),
    ("My landlord will not return my security deposit", "deposit_recovery"),

    # Money and credit
    ("Recovery agents are calling my relatives at night", "loan_recovery_agents"),
    ("There is a wrong default entry on my credit report", "credit_score_dispute"),
    ("Money was debited by UPI without my approval", "digital_payment_fraud"),
    ("The bank ignored my complaint for a month", "banking_ombudsman"),
    ("Where do I escalate a rejected insurance claim?", "insurance_ombudsman"),
    ("A company has not paid my small business in 45 days", "msme_delayed_payment"),

    # Work
    ("My employer deducted PF but never deposited it", "provident_fund"),
    ("Am I covered by ESI and what does it pay for?", "esi_benefits"),
    ("Do I get double pay for overtime?", "working_hours_overtime"),
    ("I was laid off without notice or compensation", "retrenchment_notice"),
    ("What protection do delivery and cab platform workers have?", "gig_platform_workers"),
    ("I am being forced to work to repay a debt", "bonded_labour"),

    # Health and education
    ("The surgery went wrong, can I sue the doctor?", "medical_negligence"),
    ("The hospital will not give me my case papers", "patient_rights"),
    ("Can a private school give free seats under RTE?", "rte_admission"),
    ("Seniors are ragging me in the hostel", "ragging"),

    # Family
    ("We are of different religions and want to marry", "special_marriage_act"),
    ("How do I get a marriage certificate?", "marriage_registration"),
    ("Who gets custody of our child after separation?", "child_custody"),
    ("What is the lawful process to adopt a child?", "adoption"),
    ("Do I have rights in a live-in relationship?", "live_in_relationship"),
    ("My relatives are marrying off a 16 year old girl", "child_marriage"),
    ("How do I change my gender on official documents?", "transgender_rights"),
    ("Where can a woman facing violence get immediate help?", "one_stop_centre"),

    # Criminal
    # Deliberately not phrased around a flat: money taken by a builder is a RERA
    # matter as much as a cheating one, so that wording tests nothing.
    ("He took my money promising a job and disappeared", "cheating_offence"),
    ("Police gave me a notice to appear instead of arresting", "notice_instead_of_arrest"),
    ("Can a victim of crime get compensation from the State?", "victim_compensation"),
    ("Someone threw acid on my cousin", "acid_attack"),
    ("A girl from my village was taken away for work and never returned",
     "human_trafficking"),

    # Everyday services
    ("My mobile operator overcharged and will not fix it", "telecom_complaint"),
    ("My electricity bill is wrong and they threaten disconnection", "electricity_complaint"),
    ("My train was cancelled, do I get a refund?", "railway_passenger_rights"),
    ("The airline denied me boarding on a confirmed ticket", "airline_passenger_rights"),

    # Identity and welfare
    ("How do I register a birth after one year?", "birth_death_certificate"),
    ("How do I get a caste and income certificate?", "caste_income_certificate"),
    ("Can a bank insist on Aadhaar to open an account?", "aadhaar_rights"),
    ("I want a job card for a hundred days of work", "mgnrega_work"),
    ("The municipality removed my hawker stall without notice", "street_vendor_rights"),

    # Digital
    ("How do I get a post about me taken down?", "social_media_grievance"),
    ("Someone made a fake profile with my photos", "online_impersonation"),

    # Personal law, wages, welfare, and the rest of the civic volume
    ("My husband pronounced triple talaq, is the marriage over?", "muslim_divorce_maintenance"),
    ("I am being paid less than the minimum wage", "minimum_wages"),
    ("How does a domestic worker register for welfare schemes?", "eshram_unorganised"),
    ("How do I get a disability certificate?", "disability_certificate"),
    ("Can I get free hospital treatment under a government scheme?", "ayushman_bharat"),
    ("A stranger recorded a video call and is demanding money", "sextortion_online"),
    ("A false criminal case was filed against me, can it be cancelled?", "fir_quashing"),
    ("We have settled, can the criminal case be withdrawn?", "compounding_offences"),
    ("My crop was destroyed by hail and the insurer refused", "crop_insurance"),
    ("The land record shows the wrong name for my field", "land_records"),
    ("How do I add my name to the voter list?", "voter_registration"),
    ("A government office is sitting on my application", "cpgrams_grievance"),
]

#: Questions that are not about Indian law. The retriever should return nothing
#: rather than reaching for the closest passage — a confident wrong answer is
#: the worst outcome for a legal tool.
#: Several of these were added after the corpus grew to 136 passages and started
#: answering them. A bigger corpus makes more incidental words available to
#: match on, so this list has to grow with it — "the best pizza in town" found
#: "Town Vending Committee" and answered a food question with street-vending law.
NEGATIVE_CASES: list[str] = [
    "What is the recipe for biryani?",
    "Who won the cricket world cup?",
    "How do I write a for loop in Python?",
    "What is the weather in Mumbai today?",
    "what is the best pizza in town",
    "Which is the best phone under 20000?",
    "Who is the captain of the Indian team?",
    "What time does the mall open?",
    "Tell me a joke",
    "best restaurants near me",
    "how to lose weight fast",
    "How do I cook rice?",
    "How tall is Mount Everest?",
    "Which movie should I watch tonight?",
]

#: Off-topic questions in the seven non-English UI languages.
#:
#: These exist because the semantic guard protects a *multilingual* embedding
#: space, and testing it only in English measures the wrong thing: English
#: off-topic questions are the ones the lexical guards already catch. Lowering
#: `MIN_DENSE_SIMILARITY` from 0.45 to 0.30 admits two of these while admitting
#: only one more English one, so without them the gate looks safer than it is.
#:
#: Worth knowing when tuning that gate: these overlap the genuine questions.
#: "ನಾಳೆ ಹವಾಮಾನ ಹೇಗಿರುತ್ತದೆ" (tomorrow's weather) scores 0.313 against the
#: corpus, while a real Tamil question about unpaid salary scores 0.237. No
#: threshold separates them; the gate is a trade-off, not a boundary.
NEGATIVE_MULTILINGUAL: list[tuple[str, str]] = [
    ("hi", "आज मौसम कैसा है"),
    ("hi", "सबसे अच्छी बिरयानी कहाँ मिलती है"),
    ("mr", "उद्या क्रिकेट सामना कधी आहे"),
    ("gu", "શ્રેષ્ઠ મોબાઇલ ફોન કયો છે"),
    ("ta", "இன்று வானிலை எப்படி இருக்கும்"),
    ("ta", "நல்ல உணவகம் எங்கே உள்ளது"),
    ("te", "ఈరోజు సినిమా ఏమిటి"),
    ("bn", "আজ খেলার স্কোর কত"),
    ("kn", "ಒಳ್ಳೆಯ ಹೋಟೆಲ್ ಎಲ್ಲಿದೆ"),
    ("kn", "ನಾಳೆ ಹವಾಮಾನ ಹೇಗಿರುತ್ತದೆ"),
]

#: The same eight questions asked in each of the seven non-English languages the
#: UI offers, against an English corpus. This is the metric that says whether a
#: Tamil speaker gets the same product an English speaker does — and it is
#: scored separately, because an aggregate dominated by English hides the
#: failure completely. It caught the case that motivated it: every language
#: asked about a landlord withholding a deposit and got the e-commerce refund
#: passage, or nothing at all.
#:
#: Several questions have more than one defensible answer — "what are my rights
#: on arrest" is served by both the statutory passage and the D.K. Basu
#: guidelines — so each case names the set that counts as correct rather than
#: forcing an arbitrary winner.
MULTILINGUAL_CASES: list[tuple[str, str, frozenset[str]]] = []


def _add_multilingual(expected: set[str], **by_language: str) -> None:
    for language, question in by_language.items():
        MULTILINGUAL_CASES.append((language, question, frozenset(expected)))


_add_multilingual(
    # Either is a correct landing. `deposit_recovery` is the better answer and
    # was written because the models kept hedging on `tenant_rights`, which caps
    # the deposit but never says how to get one back.
    {"tenant_rights", "deposit_recovery"},
    hi="मेरा मकान मालिक जमा राशि नहीं लौटा रहा",
    mr="घरमालक ठेव परत करत नाही",
    gu="મકાનમાલિક ડિપોઝિટ પરત આપતો નથી",
    ta="வீட்டு உரிமையாளர் வைப்புத் தொகையை திருப்பவில்லை",
    te="ఇంటి యజమాని డిపాజిట్ తిరిగి ఇవ్వడం లేదు",
    bn="বাড়িওয়ালা জমা ফেরত দিচ্ছে না",
    kn="ಮನೆ ಮಾಲೀಕ ಠೇವಣಿ ಹಿಂತಿರುಗಿಸುತ್ತಿಲ್ಲ",
)
_add_multilingual(
    {"arrest_rights", "dk_basu"},
    hi="मुझे गिरफ्तार किया गया मेरे अधिकार क्या हैं",
    mr="मला अटक झाली माझे हक्क काय",
    gu="મારી ધરપકડ થઈ મારા અધિકાર શું છે",
    ta="நான் கைது செய்யப்பட்டேன் என் உரிமைகள் என்ன",
    te="నన్ను అరెస్టు చేశారు నా హక్కులు ఏమిటి",
    bn="আমাকে গ্রেপ্তার করা হয়েছে আমার অধিকার কী",
    kn="ನನ್ನನ್ನು ಬಂಧಿಸಲಾಗಿದೆ ನನ್ನ ಹಕ್ಕುಗಳು ಏನು",
)
_add_multilingual(
    {"fir_refusal_remedy", "zero_fir", "fir_how_to_file"},
    hi="पुलिस एफआईआर दर्ज नहीं कर रही",
    mr="पोलीस एफआयआर नोंदवत नाहीत",
    gu="પોલીસ એફઆઈઆર નોંધતી નથી",
    ta="காவல்துறை எஃப்ஐஆர் பதிவு செய்யவில்லை",
    te="పోలీసులు ఎఫ్ఐఆర్ నమోదు చేయడం లేదు",
    bn="পুলিশ এফআইআর নথিভুক্ত করছে না",
    kn="ಪೊಲೀಸರು ಎಫ್ಐಆರ್ ದಾಖಲಿಸುತ್ತಿಲ್ಲ",
)
_add_multilingual(
    {"divorce_grounds_hindu", "divorce_mutual_consent"},
    hi="तलाक के आधार क्या हैं",
    mr="घटस्फोटाची कारणे काय आहेत",
    gu="છૂટાછેડા માટેના આધાર શું છે",
    ta="விவாகரத்துக்கான காரணங்கள் என்ன",
    te="విడాకులకు కారణాలు ఏమిటి",
    bn="বিবাহবিচ্ছেদের কারণ কী",
    kn="ವಿಚ್ಛೇದನಕ್ಕೆ ಕಾರಣಗಳು ಏನು",
)
_add_multilingual(
    {"daughters_coparcenary"},
    hi="बेटी का पैतृक संपत्ति में अधिकार",
    mr="मुलीचा वडिलोपार्जित मालमत्तेत हक्क",
    gu="દીકરીનો પૈતૃક મિલકતમાં અધિકાર",
    ta="மகளுக்கு மூதாதையர் சொத்தில் உரிமை",
    te="కుమార్తెకు పూర్వీకుల ఆస్తిలో హక్కు",
    bn="মেয়ের পৈতৃক সম্পত্তিতে অধিকার",
    kn="ಮಗಳಿಗೆ ಪಿತ್ರಾರ್ಜಿತ ಆಸ್ತಿಯಲ್ಲಿ ಹಕ್ಕು",
)
_add_multilingual(
    {"wage_theft"},
    hi="कंपनी ने मेरा वेतन नहीं दिया",
    mr="कंपनीने माझा पगार दिला नाही",
    gu="કંપનીએ મારો પગાર આપ્યો નથી",
    ta="நிறுவனம் என் சம்பளம் தரவில்லை",
    te="సంస్థ నా జీతం ఇవ్వలేదు",
    bn="কোম্পানি আমার বেতন দেয়নি",
    kn="ಕಂಪನಿ ನನ್ನ ಸಂಬಳ ನೀಡಿಲ್ಲ",
)
_add_multilingual(
    {"rti_how_to_file", "rti_appeals"},
    hi="सूचना का अधिकार आवेदन कैसे करें",
    mr="माहिती अधिकार अर्ज कसा करावा",
    gu="માહિતી અધિકાર અરજી કેવી રીતે કરવી",
    ta="தகவல் அறியும் உரிமை விண்ணப்பம் எப்படி",
    te="సమాచార హక్కు దరఖాస్తు ఎలా",
    bn="তথ্য অধিকার আবেদন কীভাবে",
    kn="ಮಾಹಿತಿ ಹಕ್ಕು ಅರ್ಜಿ ಹೇಗೆ",
)
_add_multilingual(
    {"consumer_where_to_file", "consumer_how_to_file", "e_commerce_rights"},
    hi="उपभोक्ता शिकायत कहां दर्ज करें",
    mr="ग्राहक तक्रार कुठे नोंदवावी",
    gu="ગ્રાહક ફરિયાદ ક્યાં નોંધાવવી",
    ta="நுகர்வோர் புகார் எங்கு அளிப்பது",
    te="వినియోగదారు ఫిర్యాదు ఎక్కడ",
    bn="ভোক্তা অভিযোগ কোথায়",
    kn="ಗ್ರಾಹಕ ದೂರು ಎಲ್ಲಿ",
)


def run(verbose: bool = True) -> dict[str, float]:
    # Wait for the embedding index if one is being built, so the run measures
    # the retrieval it names in its header rather than a half-loaded one.
    retriever = get_retriever(block_dense=True)

    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_rank_total = 0.0
    misses: list[tuple[str, str, list[str]]] = []

    for question, expected in CASES:
        results = retriever.search(question, top_k=3)
        ids = [r.passage.id for r in results]

        if ids[:1] == [expected]:
            hits_at_1 += 1
        if expected in ids:
            hits_at_3 += 1
            reciprocal_rank_total += 1.0 / (ids.index(expected) + 1)
        else:
            misses.append((question, expected, ids))

    total = len(CASES)
    false_positives = [q for q in NEGATIVE_CASES if retriever.search(q, top_k=3)]
    ml_false_positives = [
        f"[{lang}] {q}"
        for lang, q in NEGATIVE_MULTILINGUAL
        if retriever.search(q, top_k=3)
    ]

    # Cross-lingual, scored per language so one strong script cannot carry the
    # rest. `answered` is tracked separately from correctness: returning the
    # wrong passage and returning nothing at all are different failures, and
    # before the lexicon was expanded most languages did the latter.
    by_language: dict[str, dict[str, int]] = {}
    ml_misses: list[tuple[str, str, frozenset[str], list[str]]] = []
    for language, question, acceptable in MULTILINGUAL_CASES:
        stats = by_language.setdefault(language, {"n": 0, "hit@1": 0, "hit@3": 0, "answered": 0})
        results = retriever.search(question, top_k=3)
        ids = [r.passage.id for r in results]
        stats["n"] += 1
        if ids:
            stats["answered"] += 1
        if ids[:1] and ids[0] in acceptable:
            stats["hit@1"] += 1
        if acceptable & set(ids):
            stats["hit@3"] += 1
        else:
            ml_misses.append((language, question, acceptable, ids))

    ml_total = len(MULTILINGUAL_CASES)
    ml_hits_1 = sum(s["hit@1"] for s in by_language.values())
    ml_hits_3 = sum(s["hit@3"] for s in by_language.values())
    ml_answered = sum(s["answered"] for s in by_language.values())

    metrics = {
        "cases": float(total),
        "hit@1": hits_at_1 / total,
        "hit@3": hits_at_3 / total,
        "mrr": reciprocal_rank_total / total,
        "false_positive_rate": len(false_positives) / len(NEGATIVE_CASES),
        "ml_cases": float(ml_total),
        "ml_hit@1": ml_hits_1 / ml_total if ml_total else 0.0,
        "ml_hit@3": ml_hits_3 / ml_total if ml_total else 0.0,
        "ml_answered": ml_answered / ml_total if ml_total else 0.0,
        "ml_false_positive_rate": (
            len(ml_false_positives) / len(NEGATIVE_MULTILINGUAL)
            if NEGATIVE_MULTILINGUAL
            else 0.0
        ),
    }

    if verbose:
        print(f"\nRetrieval eval over {total} questions "
              f"({len(retriever.corpus)} passages, "
              f"dense={'on' if retriever.dense.available else 'off'})\n")
        print(f"  hit@1               {metrics['hit@1']:.1%}")
        print(f"  hit@3               {metrics['hit@3']:.1%}")
        print(f"  MRR                 {metrics['mrr']:.3f}")
        print(f"  false positives     {len(false_positives)}/{len(NEGATIVE_CASES)}")

        if misses:
            print(f"\n  {len(misses)} missed:")
            for question, expected, got in misses:
                print(f"    {question[:52]:54} want={expected}")
                print(f"      {'':52} got={got or '(nothing)'}")

        if false_positives:
            print("\n  Answered an out-of-scope question:")
            for question in false_positives:
                print(f"    {question}")

        print(f"\nCross-lingual eval over {ml_total} questions "
              f"in {len(by_language)} languages\n")
        print(f"  {'':4}  {'answered':>8}  {'hit@1':>6}  {'hit@3':>6}")
        for language in sorted(by_language):
            stats = by_language[language]
            n = stats["n"]
            print(f"  {language:4}  {stats['answered'] / n:>8.0%}  "
                  f"{stats['hit@1'] / n:>6.0%}  {stats['hit@3'] / n:>6.0%}")
        print(f"  {'all':4}  {metrics['ml_answered']:>8.0%}  "
              f"{metrics['ml_hit@1']:>6.0%}  {metrics['ml_hit@3']:>6.0%}")
        print(f"\n  off-topic, non-English   "
              f"{len(ml_false_positives)}/{len(NEGATIVE_MULTILINGUAL)} answered")
        for question in ml_false_positives:
            print(f"    {question}")

        if ml_misses:
            print(f"\n  {len(ml_misses)} missed:")
            for language, question, acceptable, got in ml_misses:
                print(f"    [{language}] {question[:44]:46} want={sorted(acceptable)}")
                print(f"      {'':50} got={got or '(nothing)'}")
        print()

    return metrics


if __name__ == "__main__":
    lexicon_problems = check_lexicon() + check_translations()
    if lexicon_problems:
        print(f"\n  {len(lexicon_problems)} malformed lexicon entries:")
        for problem in lexicon_problems:
            print(f"    {problem}")

    results = run()
    if lexicon_problems:
        sys.exit(1)
    # Non-zero exit on regression makes this usable as a CI gate. The
    # cross-lingual floor is deliberately lower than the English one: it runs a
    # lexicon against an English corpus, not a translation system.
    sys.exit(
        0
        if results["hit@3"] >= 0.85
        and results["false_positive_rate"] == 0
        and results["ml_false_positive_rate"] == 0
        and results["ml_hit@3"] >= 0.85
        and results["ml_answered"] >= 0.95
        else 1
    )
