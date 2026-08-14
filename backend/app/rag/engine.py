"""
Grounded answering over retrieved statute passages.

Generation is a convenience here, not a dependency. Retrieval already produced
the legally correct material with citations attached; the model's only job is
to phrase it for the person asking and, where needed, translate it. That
ordering is deliberate — it is why a wrong or missing API key degrades the
prose rather than the law.

Provider chain, first available wins:

  1. ``ollama``      — a model running on the same machine. No key, no quota.
  2. ``gemini``      — used only if a key is configured and the call succeeds.
  3. ``extractive``  — composes the reply directly from the passages. Always
                       works, offline, and cannot hallucinate a section number
                       because it never writes one.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from .retriever import RetrievedPassage, get_retriever

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
#: Leave unset to use whichever model the local Ollama actually has installed.
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "")
#: Generous, because the first request also pays for loading the model into
#: memory — a 26B model can take minutes cold and ~20s warm. For an interactive
#: chatbot prefer a 3B–4B model (llama3.2, gemma3:4b, qwen2.5:3b), which answers
#: in a couple of seconds and is well within what this grounded task needs.
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "300"))

#: How long a *chat* turn may wait for the local model before falling back to
#: the extractive answer. Nobody waits a minute for a chat reply, and the
#: extractive answer is real statute text with citations — a good outcome, not
#: a degraded one. Raise it only if you would rather wait than read.
#: 18s is comfortable for a warm 3B–4B model and short enough that a machine
#: running something much larger stops paying the tax on every single turn.
CHAT_BUDGET_SECONDS = float(os.environ.get("CHAT_BUDGET_SECONDS", "18"))

#: Keep weights resident so only the first request pays the load cost.
OLLAMA_KEEP_ALIVE = os.environ.get("OLLAMA_KEEP_ALIVE", "15m")

#: Resolved once per process: "" = not yet checked, None = no local model.
_resolved_model: str | None | object = ...

#: How many consecutive chat-budget timeouts before the local model is skipped,
#: and for how long. Without this, a machine whose only model is too big for the
#: budget pays the full wait on *every* turn to rediscover the same fact — the
#: user waits 18s and then reads the extractive answer that was available
#: immediately. Two strikes is enough to tell a slow model from an unlucky one,
#: and the breaker reopens on its own so a machine that was merely busy, or that
#: has since pulled a smaller model, recovers without a restart.
OLLAMA_STRIKES_BEFORE_SKIP = int(os.environ.get("OLLAMA_STRIKES", "2"))
OLLAMA_SKIP_SECONDS = float(os.environ.get("OLLAMA_SKIP_SECONDS", "600"))

_ollama_strikes = 0
_ollama_skip_until = 0.0


@dataclass
class Source:
    #: Corpus passage id. Carried so the UI can fetch the exact text the answer
    #: was built from — most `url`s point at a statute portal's front page,
    #: which proves nothing about what this particular answer relied on.
    id: str
    title: str
    citation: str
    url: str
    score: float


@dataclass
class LegalAnswer:
    reply: str
    sources: list[Source] = field(default_factory=list)
    #: Which generator produced the prose: ollama | gemini | extractive | none
    provider: str = "none"
    #: How well the corpus covered the question: high | medium | none
    grounding: str = "none"


# ── Prompt ──────────────────────────────────────────────────────────────
def _build_prompt(question: str, passages: list[RetrievedPassage], language: str) -> str:
    context = "\n\n".join(
        f"[{i + 1}] {p.passage.title}\n"
        f"Source: {p.passage.citation}\n"
        f"{p.passage.text}"
        for i, p in enumerate(passages)
    )

    return f"""You are Nyaysetu's legal information assistant for India.

WRITE THE ENTIRE REPLY IN {language.upper()}. Every sentence, including the
opening line and any headings. The passages below are in English and must be
translated as you use them; only statute names, section numbers and case names
stay as they are. This instruction outranks everything else in this prompt: a
correct answer in the wrong language is a failed answer, because the person
asking chose {language} for a reason.

Answer the user's question using ONLY the numbered passages below. These are the
authoritative text; do not add provisions, section numbers, penalties or deadlines
that do not appear in them.

Never state the name of a person, the holder of an office, a date, or a current
figure unless it appears word for word in a passage below. If you are asked who
currently holds an office and the passages explain how that office is filled
without naming anyone, explain how it is filled and say plainly that the current
holder is not recorded here. Do not answer from memory: the passages are
maintained, your recollection is not, and a name you remember is very likely to
belong to someone who has since left the post.

Deciding whether the question can be answered at all is not your job. That decision
has already been made: a scored retriever ran first, and when it finds nothing
relevant the user is told so without ever reaching you. Passages below therefore
always relate to the question, and your task is to phrase what they say — not to
re-judge whether they are good enough.

So do not open by disclaiming the passages, and never refer the user to a
District Legal Services Authority in place of an answer. A reply that disclaims and
then quotes the statute anyway is the single worst outcome here: it reads as "I
cannot help you" to someone who was one sentence away from the law that governs
their problem. If the passages speak to the general position but not the exact
detail asked, give the general position plainly and then say which specific point
is not covered.

That is about the passages, not about facts. Saying "the passages set out how
the office is filled but do not record who holds it today" is exactly right and
is not the hedge being warned against. Filling that gap from memory is the thing
to avoid.

Rules:
- Write the entire reply in {language}. This was stated above and is repeated
  because smaller models drift back to English after the first sentence.
- Keep statute names and section numbers exactly as they appear in the passages.
- Lead with the direct answer, then the detail. Short sentences.
- Expand abbreviations on first use; the reply may be read aloud.
- Use plain Markdown: bold and bullets only, no tables.
- End with a "Sources" line listing the citations you relied on.
- You give legal information, not legal advice.

PASSAGES
{context}

QUESTION
{question}
"""


# ── Providers ───────────────────────────────────────────────────────────
async def _resolve_ollama_model() -> str | None:
    """
    Find a usable local model, once.

    Hardcoding a model name means the chain silently fails on any machine that
    happens to have a different one pulled, so ask Ollama what it has. An
    explicit OLLAMA_MODEL always wins.

    Among several, the **smallest** wins rather than the first one listed. This
    is deliberate and is the opposite of the usual instinct. The model is not
    reasoning about the law here — retrieval has already produced the statute,
    and generation only rephrases it — so extra parameters buy almost nothing on
    answer quality while costing linearly in latency. A 26B model on a laptop
    took longer than the whole chat budget and fell through to the extractive
    path on nearly every request, which meant the local model was pure delay. A
    4B model answers the same question in a couple of seconds.
    """
    global _resolved_model
    if _resolved_model is not ...:
        return _resolved_model  # type: ignore[return-value]

    try:
        import httpx
    except ImportError:
        _resolved_model = None
        return None

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
    except Exception as exc:
        print(f"[rag] No local Ollama at {OLLAMA_URL} ({type(exc).__name__}). "
              f"Falling through to hosted model, then extractive answers.")
        _resolved_model = None
        return None

    if not models:
        _resolved_model = None
        return None

    # On-disk size is the best available proxy for how long a reply will take;
    # Ollama reports it for every model without needing to load one.
    by_size = sorted(models, key=lambda m: m.get("size") or 0)
    installed = [m["name"] for m in by_size]

    if OLLAMA_MODEL and OLLAMA_MODEL in installed:
        chosen = OLLAMA_MODEL
    elif OLLAMA_MODEL:
        print(f"[rag] OLLAMA_MODEL={OLLAMA_MODEL!r} is not installed; "
              f"using {installed[0]!r} instead.")
        chosen = installed[0]
    else:
        chosen = installed[0]

    gib = (by_size[0].get("size") or 0) / 2**30
    print(f"[rag] Local model in use: {chosen} ({gib:.1f} GiB, "
          f"smallest of {len(installed)}).")
    if gib > 8:
        print(f"[rag] That is large for a {CHAT_BUDGET_SECONDS:.0f}s budget and will "
              f"often time out into extractive answers. `ollama pull gemma3:4b` "
              f"gives a model this chain can actually use.")
    _resolved_model = chosen
    return chosen


async def _try_ollama(prompt: str) -> str | None:
    """Ask a locally running model. Returns None if Ollama isn't reachable."""
    global _ollama_strikes, _ollama_skip_until

    # Skip the local model entirely. Distinct from the strike counter below,
    # which only reacts after a request has already been slow: this refuses to
    # send one at all. Worth having because model quality, not availability, is
    # the reason to turn it off — a 4B model asked in Hindi who the Chief
    # Justice is will answer with a name out of its training data, which
    # `scripts/check_fabrication.py` exists to catch.
    if os.environ.get("NYAYSETU_DISABLE_OLLAMA") == "1":
        return None

    if time.monotonic() < _ollama_skip_until:
        return None

    model = await _resolve_ollama_model()
    if not model:
        return None

    import httpx

    try:
        async with httpx.AsyncClient(timeout=CHAT_BUDGET_SECONDS) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    # Reasoning traces are latency with no benefit here: the law
                    # is already retrieved, the model is only phrasing it.
                    "think": False,
                    "keep_alive": OLLAMA_KEEP_ALIVE,
                    "options": {"temperature": 0.2, "num_predict": 700},
                },
            )
            response.raise_for_status()
            text = (response.json().get("response") or "").strip()
            _ollama_strikes = 0
            return text or None
    except httpx.TimeoutException:
        _ollama_strikes += 1
        print(
            f"[rag] Local model exceeded the {CHAT_BUDGET_SECONDS:.0f}s chat budget "
            f"({_ollama_strikes}/{OLLAMA_STRIKES_BEFORE_SKIP}); answering from the "
            f"statute text instead. A 3B–4B model (ollama pull gemma3:4b) replies "
            f"in a couple of seconds."
        )
        if _ollama_strikes >= OLLAMA_STRIKES_BEFORE_SKIP:
            _ollama_skip_until = time.monotonic() + OLLAMA_SKIP_SECONDS
            print(
                f"[rag] Skipping the local model for {OLLAMA_SKIP_SECONDS / 60:.0f} "
                f"minutes so it stops costing every request "
                f"{CHAT_BUDGET_SECONDS:.0f}s to reach the same answer."
            )
        return None
    except Exception as exc:
        print(f"[rag] Local generation failed ({type(exc).__name__}): {exc}")
        return None


async def _try_gemini(prompt: str) -> str | None:
    """Ask Gemini, only if a key looks configured."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here" or len(api_key) < 20:
        return None

    def _call() -> str | None:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                # gemini-2.0-flash was decommissioned and now returns 404
                # NOT_FOUND, which showed up in the logs as a generic provider
                # failure. Override with GEMINI_MODEL when this one ages out too.
                model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config={"temperature": 0.2},
            )
            return (response.text or "").strip() or None
        except Exception as exc:
            print(f"[rag] Gemini unavailable: {exc}")
            return None

    return await asyncio.to_thread(_call)


# ── Extractive fallback ─────────────────────────────────────────────────
#: Section headings for the no-model answer, per output language.
_EXTRACTIVE_HEADINGS = {
    "English": ("Here is what the law says", "Related provisions", "Sources",
                "This is legal information, not legal advice."),
    "Hindi": ("कानून क्या कहता है", "संबंधित प्रावधान", "स्रोत",
              "यह कानूनी जानकारी है, कानूनी सलाह नहीं।"),
    "Marathi": ("कायदा काय सांगतो", "संबंधित तरतुदी", "स्रोत",
                "ही कायदेशीर माहिती आहे, कायदेशीर सल्ला नाही."),
    "Gujarati": ("કાયદો શું કહે છે", "સંબંધિત જોગવાઈઓ", "સ્રોત",
                 "આ કાનૂની માહિતી છે, કાનૂની સલાહ નથી."),
    "Tamil": ("சட்டம் என்ன சொல்கிறது", "தொடர்புடைய விதிகள்", "ஆதாரங்கள்",
              "இது சட்டத் தகவல், சட்ட ஆலோசனை அல்ல."),
    "Telugu": ("చట్టం ఏమి చెబుతుంది", "సంబంధిత నిబంధనలు", "మూలాలు",
               "ఇది న్యాయ సమాచారం, న్యాయ సలహా కాదు."),
    "Bengali": ("আইন কী বলে", "সম্পর্কিত বিধান", "সূত্র",
                "এটি আইনি তথ্য, আইনি পরামর্শ নয়।"),
    "Kannada": ("ಕಾನೂನು ಏನು ಹೇಳುತ್ತದೆ", "ಸಂಬಂಧಿತ ನಿಬಂಧನೆಗಳು", "ಮೂಲಗಳು",
                "ಇದು ಕಾನೂನು ಮಾಹಿತಿ, ಕಾನೂನು ಸಲಹೆ ಅಲ್ಲ."),
}

#: Shown when the extractive path runs but the user asked for another language.
_ENGLISH_TEXT_NOTICE = {
    "Hindi": "_कानूनी पाठ नीचे अंग्रेज़ी में दिया गया है।_",
    "Marathi": "_कायदेशीर मजकूर खाली इंग्रजीत आहे._",
    "Gujarati": "_કાનૂની લખાણ નીચે અંગ્રેજીમાં છે._",
    "Tamil": "_சட்ட உரை கீழே ஆங்கிலத்தில் உள்ளது._",
    "Telugu": "_చట్ట పాఠం క్రింద ఆంగ్లంలో ఉంది._",
    "Bengali": "_আইনি পাঠ্য নিচে ইংরেজিতে রয়েছে।_",
    "Kannada": "_ಕಾನೂನು ಪಠ್ಯ ಕೆಳಗೆ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿದೆ._",
}


def _extractive_answer(passages: list[RetrievedPassage], language: str) -> str:
    """
    Compose a reply from the passages themselves.

    Nothing here is generated, so nothing here can be invented — the trade is
    that the statute text stays in the language the corpus is written in.
    """
    lead, related, sources_label, disclaimer = _EXTRACTIVE_HEADINGS.get(
        language, _EXTRACTIVE_HEADINGS["English"]
    )

    parts: list[str] = []
    notice = _ENGLISH_TEXT_NOTICE.get(language)
    if notice:
        parts.append(notice)

    primary = passages[0].passage
    parts.append(f"**{lead}**\n\n**{primary.title}**\n{primary.text}")

    supporting = passages[1:3]
    if supporting:
        bullets = "\n".join(
            f"• **{p.passage.title}** — {p.passage.text.split('. ')[0]}."
            for p in supporting
        )
        parts.append(f"**{related}**\n{bullets}")

    citations = "\n".join(
        f"• {p.passage.citation} — {p.passage.source_url}" for p in passages[:3]
    )
    parts.append(f"**{sources_label}**\n{citations}")
    parts.append(f"_{disclaimer}_")

    return "\n\n".join(parts)


#: Returned when nothing in the corpus is a plausible match.
_NO_MATCH = {
    "English": (
        "I don't have reliable information on that in my legal reference set, and I "
        "won't guess on a legal question.\n\nTry rephrasing it, or ask about arrest "
        "rights, filing an FIR, free legal aid, consumer complaints, RTI, maintenance, "
        "divorce, property inheritance, workplace rights or cyber fraud.\n\nFor advice "
        "on your specific situation, your District Legal Services Authority provides a "
        "lawyer free of charge — call **15100**."
    ),
    "Hindi": (
        "मेरे कानूनी संदर्भ संग्रह में इस विषय पर विश्वसनीय जानकारी नहीं है, और कानूनी प्रश्न पर "
        "मैं अनुमान नहीं लगाऊँगा।\n\nकृपया प्रश्न दूसरे शब्दों में पूछें, या गिरफ्तारी के अधिकार, "
        "एफआईआर, निःशुल्क कानूनी सहायता, उपभोक्ता शिकायत, आरटीआई, भरण-पोषण, तलाक, संपत्ति "
        "उत्तराधिकार, कार्यस्थल अधिकार या साइबर धोखाधड़ी के बारे में पूछें।\n\nअपनी स्थिति पर सलाह "
        "के लिए जिला विधिक सेवा प्राधिकरण निःशुल्क वकील देता है — **15100** पर कॉल करें।"
    ),
    "Marathi": (
        "माझ्या कायदेशीर संदर्भ संग्रहात या विषयावर विश्वसनीय माहिती नाही, आणि कायदेशीर "
        "प्रश्नावर मी अंदाज बांधणार नाही.\n\nकृपया प्रश्न वेगळ्या शब्दांत विचारा, किंवा अटकेचे "
        "हक्क, एफआयआर, मोफत कायदेशीर मदत, ग्राहक तक्रार, माहिती अधिकार, पोटगी, घटस्फोट, "
        "मालमत्ता वारसा, कामाच्या ठिकाणचे हक्क किंवा सायबर फसवणूक याबद्दल विचारा.\n\nतुमच्या "
        "परिस्थितीवर सल्ल्यासाठी जिल्हा विधी सेवा प्राधिकरण मोफत वकील देते — **15100** वर "
        "फोन करा."
    ),
    "Gujarati": (
        "મારા કાનૂની સંદર્ભ સંગ્રહમાં આ વિષય પર વિશ્વસનીય માહિતી નથી, અને કાનૂની પ્રશ્ન પર "
        "હું અનુમાન નહીં કરું.\n\nકૃપા કરીને પ્રશ્ન બીજા શબ્દોમાં પૂછો, અથવા ધરપકડના અધિકાર, "
        "એફઆઈઆર, મફત કાનૂની સહાય, ગ્રાહક ફરિયાદ, માહિતી અધિકાર, ભરણપોષણ, છૂટાછેડા, "
        "મિલકત વારસો, કાર્યસ્થળના અધિકાર કે સાયબર છેતરપિંડી વિશે પૂછો.\n\nતમારી પરિસ્થિતિ "
        "પર સલાહ માટે જિલ્લા કાનૂની સેવા સત્તામંડળ મફત વકીલ આપે છે — **15100** પર કૉલ કરો."
    ),
    "Tamil": (
        "என் சட்ட மேற்கோள் தொகுப்பில் இந்த விசயத்தில் நம்பகமான தகவல் இல்லை; சட்டக் "
        "கேள்விக்கு நான் ஊகிக்க மாட்டேன்.\n\nகேள்வியை வேறு வார்த்தைகளில் கேளுங்கள், "
        "அல்லது கைது உரிமைகள், எஃப்ஐஆர், இலவச சட்ட உதவி, நுகர்வோர் புகார், தகவல் அறியும் "
        "உரிமை, ஜீவனாம்சம், விவாகரத்து, சொத்து வாரிசு, பணியிட உரிமைகள் அல்லது சைபர் மோசடி "
        "பற்றிக் கேளுங்கள்.\n\nஉங்கள் நிலைமைக்கான ஆலோசனைக்கு மாவட்ட சட்டப் பணிகள் ஆணையம் "
        "இலவசமாக வழக்கறிஞரை வழங்குகிறது — **15100** ஐ அழைக்கவும்."
    ),
    "Telugu": (
        "నా న్యాయ సూచన సంకలనంలో ఈ విషయంపై విశ్వసనీయ సమాచారం లేదు, మరియు న్యాయ "
        "ప్రశ్నపై నేను ఊహించను.\n\nప్రశ్నను వేరే మాటల్లో అడగండి, లేదా అరెస్టు హక్కులు, "
        "ఎఫ్ఐఆర్, ఉచిత న్యాయ సహాయం, వినియోగదారు ఫిర్యాదు, సమాచార హక్కు, భరణం, విడాకులు, "
        "ఆస్తి వారసత్వం, కార్యాలయ హక్కులు లేదా సైబర్ మోసం గురించి అడగండి.\n\nమీ పరిస్థితిపై "
        "సలహా కోసం జిల్లా న్యాయ సేవల ప్రాధికార సంస్థ ఉచితంగా న్యాయవాదిని ఇస్తుంది — "
        "**15100** కు కాల్ చేయండి."
    ),
    "Bengali": (
        "আমার আইনি তথ্যভাণ্ডারে এই বিষয়ে নির্ভরযোগ্য তথ্য নেই, এবং আইনি প্রশ্নে আমি "
        "অনুমান করব না।\n\nঅনুগ্রহ করে প্রশ্নটি অন্য ভাষায় জিজ্ঞাসা করুন, অথবা গ্রেপ্তারের "
        "অধিকার, এফআইআর, বিনামূল্যে আইনি সহায়তা, ভোক্তা অভিযোগ, তথ্য অধিকার, ভরণপোষণ, "
        "বিবাহবিচ্ছেদ, সম্পত্তির উত্তরাধিকার, কর্মক্ষেত্রের অধিকার বা সাইবার প্রতারণা সম্পর্কে "
        "জিজ্ঞাসা করুন।\n\nআপনার পরিস্থিতির পরামর্শের জন্য জেলা আইনি পরিষেবা কর্তৃপক্ষ "
        "বিনামূল্যে আইনজীবী দেয় — **15100** নম্বরে ফোন করুন।"
    ),
    "Kannada": (
        "ನನ್ನ ಕಾನೂನು ಉಲ್ಲೇಖ ಸಂಗ್ರಹದಲ್ಲಿ ಈ ವಿಷಯದ ಬಗ್ಗೆ ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿ ಇಲ್ಲ, ಮತ್ತು "
        "ಕಾನೂನು ಪ್ರಶ್ನೆಯ ಮೇಲೆ ನಾನು ಊಹಿಸುವುದಿಲ್ಲ.\n\nದಯವಿಟ್ಟು ಪ್ರಶ್ನೆಯನ್ನು ಬೇರೆ ಪದಗಳಲ್ಲಿ "
        "ಕೇಳಿ, ಅಥವಾ ಬಂಧನದ ಹಕ್ಕುಗಳು, ಎಫ್ಐಆರ್, ಉಚಿತ ಕಾನೂನು ನೆರವು, ಗ್ರಾಹಕ ದೂರು, ಮಾಹಿತಿ "
        "ಹಕ್ಕು, ಜೀವನಾಂಶ, ವಿಚ್ಛೇದನ, ಆಸ್ತಿ ಉತ್ತರಾಧಿಕಾರ, ಕೆಲಸದ ಸ್ಥಳದ ಹಕ್ಕುಗಳು ಅಥವಾ ಸೈಬರ್ "
        "ವಂಚನೆಯ ಬಗ್ಗೆ ಕೇಳಿ.\n\nನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಗೆ ಸಲಹೆಗಾಗಿ ಜಿಲ್ಲಾ ಕಾನೂನು ಸೇವಾ ಪ್ರಾಧಿಕಾರ "
        "ಉಚಿತವಾಗಿ ವಕೀಲರನ್ನು ನೀಡುತ್ತದೆ — **15100** ಗೆ ಕರೆ ಮಾಡಿ."
    ),
}


def _no_match_reply(language: str) -> str:
    return _NO_MATCH.get(language, _NO_MATCH["English"])


def _topic_neighbours(pinned, limit: int = 2) -> list[RetrievedPassage]:
    """
    Find genuinely related passages to cite alongside a pinned one.

    Lexical search is the wrong tool here. A title like "Your rights when you
    are arrested" reduces to two useful tokens, and BM25 on a query that thin
    will happily return the basic structure doctrine because it also says
    "rights". Shared topic tags are curated and mean what they say, so they
    pick neighbours that a lawyer would actually cite together.
    """
    from .corpus import CORPUS

    pinned_topics = set(pinned.topics)
    if not pinned_topics:
        return []

    scored: list[tuple[int, object]] = []
    for candidate in CORPUS:
        if candidate.id == pinned.id:
            continue
        overlap = len(pinned_topics & set(candidate.topics))
        if overlap:
            scored.append((overlap, candidate))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        RetrievedPassage(
            passage=candidate,
            score=round(min(0.9, 0.45 + 0.15 * overlap), 4),
            matched_by=("topic",),
        )
        for overlap, candidate in scored[:limit]
    ]


#: Unicode ranges for the scripts the UI offers, used to check that a generated
#: reply is actually in the language the user asked for.
_SCRIPT_RANGES: dict[str, tuple[int, int]] = {
    "Hindi": (0x0900, 0x097F),
    "Marathi": (0x0900, 0x097F),
    "Gujarati": (0x0A80, 0x0AFF),
    "Tamil": (0x0B80, 0x0BFF),
    "Telugu": (0x0C00, 0x0C7F),
    "Bengali": (0x0980, 0x09FF),
    "Kannada": (0x0C80, 0x0CFF),
}

#: Share of letters that must be in the target script. Well under half on
#: purpose: a correct reply legitimately carries English statute names, section
#: numbers and URLs ("Model Tenancy Act, 2021"), so the test is meant to catch a
#: reply that ignored the language entirely, not one that quotes an Act.
_MIN_TARGET_SCRIPT_SHARE = 0.25


def _is_in_requested_language(reply: str, language: str) -> bool:
    """
    Check a generated reply is written in the script that was asked for.

    Small local models follow a language instruction unreliably — a 4B model
    asked for Hindi will often answer in English, and the user has no way to
    retry into a different provider. Rather than trust the instruction, verify
    the output and let the caller fall through to the next generator, which is
    the same principle the rest of this module runs on: check, do not assume.
    """
    target = _SCRIPT_RANGES.get(language)
    if target is None:  # English, or a language we cannot check
        return True

    low, high = target
    letters = in_target = 0
    for char in reply:
        if not char.isalpha():
            continue
        letters += 1
        if low <= ord(char) <= high:
            in_target += 1
    if letters < 40:  # too short to judge; do not reject on noise
        return True
    return (in_target / letters) >= _MIN_TARGET_SCRIPT_SHARE


def _select_passages(question: str, topic: str | None) -> list[RetrievedPassage]:
    """
    Choose the passages an answer will be built from.

    `topic` pins retrieval to a known passage id — used by the translated
    suggestion chips, whose text would otherwise have to match the corpus
    across eight scripts. Shared by the streaming and non-streaming paths so
    they can never disagree about what the answer is grounded in.
    """
    if topic:
        from .corpus import get as get_passage

        pinned = get_passage(topic)
        if pinned:
            return [
                RetrievedPassage(passage=pinned, score=1.0, matched_by=("topic",)),
                *_topic_neighbours(pinned, limit=2),
            ]

    return get_retriever().search(question, top_k=4)


# ── Public entry point ──────────────────────────────────────────────────
async def answer_question(
    question: str,
    language: str = "English",
    topic: str | None = None,
) -> LegalAnswer:
    """Retrieve, then phrase."""
    passages = _select_passages(question, topic)

    if not passages:
        return LegalAnswer(reply=_no_match_reply(language), provider="none", grounding="none")

    sources = [
        Source(
            id=p.passage.id,
            title=p.passage.title,
            citation=p.passage.citation,
            url=p.passage.source_url,
            score=p.score,
        )
        for p in passages[:3]
    ]
    # Confidence, not score. `score` is relative — the best result is 1.0 even
    # when it is the best of a weak field — so thresholding it graded almost
    # everything "high". `confidence` is absolute and says whether the evidence
    # was actually strong.
    grounding = "high" if passages[0].confidence >= 0.55 else "medium"

    prompt = _build_prompt(question, passages, language)

    generated = await _try_ollama(prompt)
    if generated and not _is_in_requested_language(generated, language):
        print(f"[rag] Local model replied in the wrong language (wanted {language}); "
              f"trying the next provider.")
        generated = None
    if generated:
        return LegalAnswer(reply=generated, sources=sources, provider="ollama", grounding=grounding)

    generated = await _try_gemini(prompt)
    if generated and not _is_in_requested_language(generated, language):
        print(f"[rag] Hosted model replied in the wrong language (wanted {language}); "
              f"falling back to the extractive answer.")
        generated = None
    if generated:
        return LegalAnswer(reply=generated, sources=sources, provider="gemini", grounding=grounding)

    return LegalAnswer(
        reply=_extractive_answer(passages, language),
        sources=sources,
        provider="extractive",
        grounding=grounding,
    )


# ── Streaming ───────────────────────────────────────────────────────────
async def stream_answer(
    question: str,
    language: str = "English",
    topic: str | None = None,
) -> AsyncIterator[dict]:
    """
    Same answer, delivered incrementally.

    A local model's *total* time is dominated by how many tokens it writes, but
    its time-to-first-token is short. Streaming turns a 40-second stare at a
    spinner into text appearing in about a second and continuing to arrive —
    the reply takes just as long, but the reader is never blocked on it.

    Yields dicts: {"type": "sources"|"delta"|"done", ...}
    """
    passages = _select_passages(question, topic)

    if not passages:
        yield {"type": "delta", "text": _no_match_reply(language)}
        yield {"type": "done", "provider": "none", "grounding": "none"}
        return

    sources = [
        {
            "id": p.passage.id,
            "title": p.passage.title,
            "citation": p.passage.citation,
            "url": p.passage.source_url,
        }
        for p in passages[:3]
    ]
    # Confidence, not score. `score` is relative — the best result is 1.0 even
    # when it is the best of a weak field — so thresholding it graded almost
    # everything "high". `confidence` is absolute and says whether the evidence
    # was actually strong.
    grounding = "high" if passages[0].confidence >= 0.55 else "medium"

    # Send citations before a single token of prose. They are already known, and
    # showing what the answer rests on while it is still being written is a
    # better order for a legal tool than the other way round.
    yield {"type": "sources", "sources": sources, "grounding": grounding}

    prompt = _build_prompt(question, passages, language)

    model = await _resolve_ollama_model()
    if model:
        streamed_any = False
        try:
            import httpx

            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "think": False,
                        "keep_alive": OLLAMA_KEEP_ALIVE,
                        "options": {"temperature": 0.2, "num_predict": 700},
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        piece = chunk.get("response") or ""
                        if piece:
                            streamed_any = True
                            yield {"type": "delta", "text": piece}
                        if chunk.get("done"):
                            break

            if streamed_any:
                yield {"type": "done", "provider": "ollama", "grounding": grounding}
                return
        except Exception as exc:
            print(f"[rag] Streaming failed ({type(exc).__name__}): {exc}")
            if streamed_any:
                # Partial output already reached the client; ending here beats
                # appending a second, differently-worded answer underneath it.
                yield {"type": "done", "provider": "ollama", "grounding": grounding}
                return

    generated = await _try_gemini(prompt)
    if generated:
        yield {"type": "delta", "text": generated}
        yield {"type": "done", "provider": "gemini", "grounding": grounding}
        return

    yield {"type": "delta", "text": _extractive_answer(passages, language)}
    yield {"type": "done", "provider": "extractive", "grounding": grounding}
