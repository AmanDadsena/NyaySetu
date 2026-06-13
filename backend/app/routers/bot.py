import os
import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

router = APIRouter(prefix="/api/bot", tags=["bot"])

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    status: str
    reply: str

# ── Built-in Legal Knowledge Base (Offline Fallback) ────────────────────────
# Curated, accurate answers sourced from official Indian legal references.
# This ensures the chatbot always works, even without an API key.

LEGAL_FAQ_DB = [
    {
        "keywords": ["free legal aid", "nalsa", "legal services", "free lawyer", "poor", "legal help"],
        "answer": (
            "**Free Legal Aid in India (NALSA)**\n\n"
            "Under **Section 12 of the Legal Services Authorities Act, 1987**, free legal aid is available to:\n\n"
            "• Members of Scheduled Castes or Scheduled Tribes\n"
            "• Victims of trafficking or bonded labour\n"
            "• Women and children\n"
            "• Persons with disabilities\n"
            "• Persons with annual income below ₹3,00,000 (may vary by state)\n"
            "• Industrial workmen\n"
            "• Persons in custody\n"
            "• Victims of mass disasters, ethnic violence, or caste atrocities\n\n"
            "**How to apply:**\n"
            "1. Visit your nearest **District Legal Services Authority (DLSA)** office\n"
            "2. Apply online at **nalsa.gov.in**\n"
            "3. Call the NALSA helpline: **15100**\n"
            "4. Visit a **Lok Adalat** or **Legal Aid Clinic** in your area\n\n"
            "📌 *Source: Legal Services Authorities Act, 1987 (Section 12) — nalsa.gov.in*"
        ),
    },
    {
        "keywords": ["fir", "file fir", "first information report", "police complaint", "police report"],
        "answer": (
            "**How to File an FIR (First Information Report)**\n\n"
            "An FIR is a written document prepared by police when they receive information about a **cognizable offence** "
            "(under **Section 173 of BNSS, 2023** — formerly Section 154 of CrPC).\n\n"
            "**Steps to file an FIR:**\n"
            "1. Visit the **nearest police station** (the one having jurisdiction over the area where the offence occurred)\n"
            "2. Provide details of the incident orally or in writing\n"
            "3. The police officer **must register the FIR** — refusal is an offence under **Section 166A IPC / Section 170 BNS**\n"
            "4. Get a **free copy of the FIR** — this is your legal right\n"
            "5. If police refuse, file a complaint with the **Superintendent of Police (SP)** or approach the **Magistrate under Section 175(3) BNSS**\n\n"
            "**Zero FIR:** You can file an FIR at **any police station** regardless of jurisdiction. It will be transferred to the correct station.\n\n"
            "**E-FIR:** Many states now allow filing FIRs online through their respective police portals.\n\n"
            "📌 *Source: Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 — Section 173*"
        ),
    },
    {
        "keywords": ["arrest", "arrested", "rights if arrested", "rights arrest", "police arrest", "detention"],
        "answer": (
            "**Your Fundamental Rights if Arrested**\n\n"
            "Under the **Constitution of India** and the **Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**:\n\n"
            "• **Right to know the grounds of arrest** — The police must inform you why you are being arrested "
            "(Article 22(1) of the Constitution, Section 47 BNSS)\n"
            "• **Right to legal counsel** — You have the right to consult and be defended by a lawyer of your choice "
            "(Article 22(1))\n"
            "• **Right to free legal aid** — If you cannot afford a lawyer, one must be provided at State expense "
            "(Section 12, Legal Services Authorities Act, 1987)\n"
            "• **Right to be produced before a Magistrate within 24 hours** — excluding travel time "
            "(Article 22(2), Section 58 BNSS)\n"
            "• **Right against self-incrimination** — You cannot be compelled to be a witness against yourself "
            "(Article 20(3))\n"
            "• **Right to inform family/friend** — Police must inform a nominated person of your arrest "
            "(Section 36 BNSS)\n"
            "• **Right to medical examination** — Available under Section 51 BNSS\n"
            "• **Protection from torture** — No person in custody shall be subjected to torture or cruel treatment\n\n"
            "**Important:** The landmark judgment **D.K. Basu v. State of West Bengal (1997)** laid down 11 mandatory guidelines "
            "that police must follow during arrest.\n\n"
            "📌 *Source: Constitution of India (Art. 20-22), BNSS 2023, D.K. Basu v. State of West Bengal (1997) 1 SCC 416*"
        ),
    },
    {
        "keywords": ["consumer court", "consumer complaint", "consumer forum", "consumer rights", "consumer protection", "defective product", "deficient service"],
        "answer": (
            "**How to File a Consumer Complaint**\n\n"
            "Under the **Consumer Protection Act, 2019**, you can file a complaint for:\n"
            "• Defective goods or deficient services\n"
            "• Unfair trade practices or misleading advertisements\n"
            "• Overcharging (beyond MRP)\n\n"
            "**Where to file (based on value of goods/services):**\n"
            "• Up to ₹1 Crore → **District Consumer Disputes Redressal Commission**\n"
            "• ₹1 Crore to ₹10 Crore → **State Consumer Disputes Redressal Commission**\n"
            "• Above ₹10 Crore → **National Consumer Disputes Redressal Commission (NCDRC)**\n\n"
            "**Steps:**\n"
            "1. Send a written notice to the seller/service provider first\n"
            "2. File online at **edaakhil.nic.in** (National Consumer Helpline portal)\n"
            "3. Attach bills, receipts, warranty cards, and communication records\n"
            "4. Pay nominal court fees\n"
            "5. You can also call the **Consumer Helpline: 1915** (formerly 1800-11-4000)\n\n"
            "**No lawyer required** — You can argue your own case before the Consumer Forum.\n\n"
            "📌 *Source: Consumer Protection Act, 2019 — consumerhelpline.gov.in, edaakhil.nic.in*"
        ),
    },
    {
        "keywords": ["bns", "bharatiya nyaya sanhita", "new penal code", "ipc replaced", "new criminal law"],
        "answer": (
            "**Bharatiya Nyaya Sanhita (BNS), 2023 — Key Changes**\n\n"
            "The BNS replaced the **Indian Penal Code (IPC), 1860** and came into effect on **1 July 2024**.\n\n"
            "**Major changes:**\n"
            "• **Sections reduced** from 511 (IPC) to 358 (BNS) by removing obsolete colonial provisions\n"
            "• **Sedition repealed** — The old Section 124A IPC (sedition) has been removed. "
            "A new Section 152 BNS addresses acts endangering sovereignty with stricter definitions\n"
            "• **Community service** introduced as a new form of punishment for certain petty offences (Section 4(f) BNS)\n"
            "• **Crimes against women & children** are prioritized and grouped into a dedicated chapter\n"
            "• **Organized crime & terrorism** defined for the first time in the penal code (Section 111-113 BNS)\n"
            "• **Mob lynching** now a specific offence under Section 103(2) BNS\n"
            "• **Gender-neutral laws** for certain offences that were previously gendered\n"
            "• **Snatching** introduced as a distinct offence (Section 304 BNS)\n"
            "• **Hit and run** has enhanced penalties under Section 106(2) BNS\n\n"
            "**Companion laws enacted simultaneously:**\n"
            "• **Bharatiya Nagarik Suraksha Sanhita (BNSS)** — replaces CrPC\n"
            "• **Bharatiya Sakshya Adhiniyam (BSA)** — replaces Indian Evidence Act\n\n"
            "📌 *Source: Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023) — indiacode.nic.in*"
        ),
    },
    {
        "keywords": ["fundamental rights", "constitution", "basic rights", "part 3", "article 14", "article 19", "article 21"],
        "answer": (
            "**Fundamental Rights (Part III of the Constitution of India)**\n\n"
            "These are guaranteed under **Articles 12 to 35** and are enforceable by the Supreme Court "
            "under **Article 32** (and High Courts under **Article 226**):\n\n"
            "1. **Right to Equality (Art. 14–18)**\n"
            "   • Equality before law, prohibition of discrimination on grounds of religion, race, caste, sex, or place of birth\n"
            "   • Abolition of untouchability (Art. 17) and titles (Art. 18)\n\n"
            "2. **Right to Freedom (Art. 19–22)**\n"
            "   • Freedom of speech, assembly, association, movement, residence, and profession\n"
            "   • Protection against arbitrary arrest (Art. 22)\n\n"
            "3. **Right against Exploitation (Art. 23–24)**\n"
            "   • Prohibition of forced labour and child labour in hazardous conditions\n\n"
            "4. **Right to Freedom of Religion (Art. 25–28)**\n"
            "   • Freedom of conscience and free profession, practice, and propagation of religion\n\n"
            "5. **Cultural and Educational Rights (Art. 29–30)**\n"
            "   • Protection of interests of minorities\n\n"
            "6. **Right to Constitutional Remedies (Art. 32)**\n"
            "   • Called the \"heart and soul\" of the Constitution by Dr. B.R. Ambedkar\n"
            "   • Writs: Habeas Corpus, Mandamus, Prohibition, Certiorari, Quo Warranto\n\n"
            "📌 *Source: Constitution of India, Part III — legislative.gov.in*"
        ),
    },
    {
        "keywords": ["divorce", "marriage", "separation", "matrimonial", "maintenance", "alimony"],
        "answer": (
            "**Divorce Laws in India**\n\n"
            "Divorce laws in India vary by religion:\n\n"
            "• **Hindu Marriage Act, 1955** — Governs Hindus, Buddhists, Jains, Sikhs\n"
            "• **Muslim Personal Law (Shariat) Application Act, 1937** — Governs Muslims\n"
            "• **Indian Christian Marriage Act, 1872 & Indian Divorce Act, 1869** — Governs Christians\n"
            "• **Special Marriage Act, 1954** — For inter-faith or civil marriages\n\n"
            "**Grounds for divorce (Hindu Marriage Act):**\n"
            "Adultery, cruelty, desertion (2+ years), conversion, mental disorder, communicable disease, "
            "renunciation of the world, not heard alive for 7 years.\n\n"
            "**Mutual consent divorce** (Section 13B) requires:\n"
            "• Both parties agree to separate\n"
            "• Living separately for at least 1 year\n"
            "• A 6-month cooling-off period (can be waived by court in certain cases per Supreme Court ruling in *Amardeep Singh v. Harveen Kaur, 2017*)\n\n"
            "**Maintenance:** Under **Section 125 BNSS** (formerly CrPC), a wife, children, and parents can claim maintenance regardless of religion.\n\n"
            "📌 *Source: Hindu Marriage Act 1955, Special Marriage Act 1954, BNSS 2023 (Section 144)*"
        ),
    },
    {
        "keywords": ["property", "land", "inheritance", "succession", "will", "property rights"],
        "answer": (
            "**Property & Inheritance Laws in India**\n\n"
            "**For Hindus (Hindu Succession Act, 1956, amended 2005):**\n"
            "• **Daughters have equal coparcenary rights** in ancestral property (2005 Amendment)\n"
            "• This was reinforced by the Supreme Court in **Vineeta Sharma v. Rakesh Sharma (2020)**\n"
            "• Applies to all Hindu joint family (HUF) properties\n\n"
            "**For Muslims (Muslim Personal Law):**\n"
            "• Governed by Sharia principles\n"
            "• Daughters typically inherit half the share of sons\n"
            "• Will (Wasiyat) can dispose of up to 1/3rd of property\n\n"
            "**For Christians & Others (Indian Succession Act, 1925):**\n"
            "• If a person dies without a will, the estate is distributed per the Act\n\n"
            "**Transfer of Property Act, 1882** governs sale, mortgage, lease, and gift of immovable property.\n\n"
            "**Registration:** All property transfers must be registered under the **Registration Act, 1908** at the Sub-Registrar's office.\n\n"
            "📌 *Source: Hindu Succession Act 1956, Transfer of Property Act 1882, Indian Succession Act 1925*"
        ),
    },
    {
        "keywords": ["rti", "right to information", "information act", "government information"],
        "answer": (
            "**Right to Information (RTI) Act, 2005**\n\n"
            "Every citizen of India has the right to seek information from any **public authority**.\n\n"
            "**How to file an RTI:**\n"
            "1. Write a simple application addressed to the **Public Information Officer (PIO)** of the department\n"
            "2. Pay a fee of **₹10** (by postal order, DD, or online)\n"
            "3. You can file online at **rtionline.gov.in** for Central Government departments\n"
            "4. For State Government, visit the respective state RTI portal\n\n"
            "**Response timeline:**\n"
            "• **30 days** for normal requests\n"
            "• **48 hours** if the information concerns the life or liberty of a person\n\n"
            "**First Appeal:** If unsatisfied, appeal to the **First Appellate Authority** within 30 days\n"
            "**Second Appeal:** To the **Central/State Information Commission** within 90 days\n\n"
            "**Penalty:** Officers can be penalized **₹250/day** (up to ₹25,000) for delays without reasonable cause.\n\n"
            "📌 *Source: Right to Information Act, 2005 — rtionline.gov.in*"
        ),
    },
    {
        "keywords": ["cyber crime", "online fraud", "hacking", "cyber", "it act", "internet crime", "online harassment"],
        "answer": (
            "**Cyber Crime Laws in India**\n\n"
            "Governed primarily by the **Information Technology Act, 2000** (IT Act) and the **BNS, 2023**:\n\n"
            "**Common cyber offences:**\n"
            "• **Hacking** — Section 66 IT Act (up to 3 years imprisonment + fine)\n"
            "• **Identity theft** — Section 66C IT Act\n"
            "• **Cyber stalking/bullying** — Section 354D BNS (formerly IPC)\n"
            "• **Publishing obscene content** — Section 67/67A/67B IT Act\n"
            "• **Online fraud / cheating** — Section 318 BNS + Section 66D IT Act\n"
            "• **Data breach** — Section 43A IT Act\n\n"
            "**How to report:**\n"
            "1. File a complaint at **cybercrime.gov.in** (National Cyber Crime Reporting Portal)\n"
            "2. Call the **Cyber Crime Helpline: 1930**\n"
            "3. Visit the nearest **Cyber Crime Police Station**\n"
            "4. Preserve all digital evidence (screenshots, emails, URLs, transaction IDs)\n\n"
            "📌 *Source: Information Technology Act, 2000 — cybercrime.gov.in*"
        ),
    },
    {
        "keywords": ["labour", "labor", "employment", "wages", "minimum wage", "worker rights", "employee"],
        "answer": (
            "**Labour & Employment Laws in India**\n\n"
            "India has consolidated its labour laws into **4 Labour Codes** (enacted 2019-2020):\n\n"
            "1. **Code on Wages, 2019** — Covers minimum wages, payment of wages, bonus, and equal remuneration\n"
            "2. **Industrial Relations Code, 2020** — Trade unions, standing orders, industrial disputes\n"
            "3. **Code on Social Security, 2020** — EPF, ESI, gratuity, maternity benefits\n"
            "4. **Occupational Safety, Health & Working Conditions Code, 2020**\n\n"
            "**Key rights:**\n"
            "• **Minimum Wages** are set by both Central and State governments\n"
            "• **Working hours**: Generally 8 hours/day, 48 hours/week\n"
            "• **Gratuity**: After 5 years of continuous service (Payment of Gratuity Act, 1972)\n"
            "• **Maternity leave**: 26 weeks for first 2 children (Maternity Benefit Act, 1961 as amended)\n"
            "• **Equal pay for equal work** regardless of gender\n\n"
            "📌 *Source: The 4 Labour Codes (2019-2020) — labour.gov.in*"
        ),
    },
    {
        "keywords": ["traffic", "challan", "e-challan", "motor vehicle", "driving license", "traffic fine", "traffic law"],
        "answer": (
            "**Traffic & Motor Vehicle Laws**\n\n"
            "Governed by the **Motor Vehicles Act, 1988** (amended 2019):\n\n"
            "**Key penalties (after 2019 amendment):**\n"
            "• Driving without license — ₹5,000 (was ₹500)\n"
            "• Driving without insurance — ₹2,000 (was ₹1,000)\n"
            "• Drunk driving — ₹10,000 (was ₹2,000)\n"
            "• Overspeeding — ₹1,000-₹2,000 (was ₹400)\n"
            "• Not wearing seatbelt — ₹1,000 (was ₹100)\n"
            "• Using mobile while driving — ₹5,000\n"
            "• Juvenile driving — ₹25,000 + 3 years imprisonment for guardian\n\n"
            "**E-Challan system:** Most states use interconnected digital challan systems. "
            "Check and pay pending challans at **echallan.parivahan.gov.in**\n\n"
            "**Driving license:** Apply online at **parivahan.gov.in** (Sarathi portal)\n\n"
            "📌 *Source: Motor Vehicles (Amendment) Act, 2019 — parivahan.gov.in*"
        ),
    },
    {
        "keywords": ["nyaysetu", "what is nyaysetu", "about nyaysetu", "this website", "platform", "features"],
        "answer": (
            "**Welcome to Nyaysetu! 🏛️**\n\n"
            "Nyaysetu is an AI-powered legal technology platform designed to make Indian law accessible to everyone.\n\n"
            "**Our Features:**\n"
            "• **Document Analysis** — Upload legal documents (PDF, DOCX, or text) and get AI-powered clause extraction, "
            "risk analysis, and plain-language summaries\n"
            "• **Find Lawyers** — Connect with legal professionals based on specialization and experience\n"
            "• **Case Discussions** — Secure messaging for case-related discussions\n"
            "• **Legal Knowledge Base** — Curated information on the Constitution of India, BNS 2023, and more\n"
            "• **AI Legal Assistant** — This chatbot! Ask me anything about Indian law.\n\n"
            "Use the navigation bar above to explore these features, or ask me a legal question right here!"
        ),
    },
    {
        "keywords": ["landmark", "important cases", "kesavananda", "basic structure"],
        "answer": (
            "**Landmark Indian Judgments: Kesavananda Bharati (1973)**\n\n"
            "In *Kesavananda Bharati v. State of Kerala (1973)*, a 13-judge bench of the Supreme Court established the **Basic Structure Doctrine**.\n\n"
            "**Key Ruling:**\n"
            "While Parliament has the power to amend the Constitution (under Article 368), it cannot alter or destroy its 'basic structure'.\n\n"
            "This historic judgment ensured that the foundational principles of India—such as democracy, secularism, separation of powers, and judicial review—cannot be erased by a legislative majority, thereby saving Indian democracy from authoritarian overreach."
        ),
    },
    {
        "keywords": ["maneka gandhi", "right to life", "personal liberty", "article 21 case"],
        "answer": (
            "**Landmark Indian Judgments: Maneka Gandhi (1978)**\n\n"
            "In *Maneka Gandhi v. Union of India (1978)*, the Supreme Court dramatically expanded the scope of **Article 21 (Right to Life and Personal Liberty)**.\n\n"
            "**Key Ruling:**\n"
            "The Court ruled that the 'procedure established by law' used to deprive someone of their liberty must be **just, fair, and reasonable**, not arbitrary or oppressive.\n\n"
            "This judgment interlinked Articles 14, 19, and 21 (the 'Golden Triangle') and expanded the right to life to include the right to travel abroad, right to dignity, and eventually right to privacy and clean environment."
        ),
    },
    {
        "keywords": ["shah bano", "triple talaq", "maintenance for muslim women", "uniform civil code"],
        "answer": (
            "**Landmark Indian Judgments: Shah Bano Case (1985)**\n\n"
            "In *Mohd. Ahmed Khan v. Shah Bano Begum (1985)*, the Supreme Court ruled in favor of a divorced Muslim woman seeking maintenance from her former husband.\n\n"
            "**Key Ruling:**\n"
            "The Court held that **Section 125 of the Code of Criminal Procedure** (which provides for maintenance to wives, children, and parents) applies to all citizens regardless of religion, overriding personal laws.\n\n"
            "This sparked a massive national debate on the Uniform Civil Code (UCC) and the balance between personal religious laws and secular criminal law."
        ),
    },
    {
        "keywords": ["vishaka", "sexual harassment", "posh act", "workplace safety"],
        "answer": (
            "**Landmark Indian Judgments: Vishaka Guidelines (1997)**\n\n"
            "In *Vishaka v. State of Rajasthan (1997)*, the Supreme Court laid down mandatory guidelines to prevent sexual harassment of women at the workplace.\n\n"
            "**Key Ruling:**\n"
            "In the absence of domestic law, the Court formulated the **Vishaka Guidelines** making it mandatory for employers to provide a safe working environment and set up complaint mechanisms.\n\n"
            "These guidelines eventually led to the enactment of the **Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013 (POSH Act)**."
        ),
    },
    {
        "keywords": ["privacy", "puttaswamy", "aadhaar case", "right to privacy"],
        "answer": (
            "**Landmark Indian Judgments: Right to Privacy (2017)**\n\n"
            "In *Justice K.S. Puttaswamy (Retd.) v. Union of India (2017)*, a 9-judge bench unanimously ruled that the **Right to Privacy** is a fundamental right.\n\n"
            "**Key Ruling:**\n"
            "Privacy is intrinsically protected as a part of the Right to Life and Personal Liberty under **Article 21** and as a part of the freedoms guaranteed by Part III of the Constitution.\n\n"
            "This monumental ruling has since influenced laws concerning data protection, surveillance, and the decriminalization of homosexuality (Section 377)."
        ),
    }
]


def _find_faq_answer(query: str) -> Optional[str]:
    """
    Perform keyword-based matching against the built-in FAQ database.
    Returns the best matching answer or None if no match is found.
    """
    query_lower = query.lower().strip()
    best_match = None
    best_score = 0

    for faq in LEGAL_FAQ_DB:
        score = sum(1 for kw in faq["keywords"] if kw in query_lower)
        if score > best_score:
            best_score = score
            best_match = faq["answer"]

    # Require at least one keyword match
    if best_score >= 1:
        return best_match
    return None


def _get_generic_response() -> str:
    """Return a helpful generic response when no FAQ match is found and the API is unavailable."""
    return (
        "I appreciate your question! While I don't have a specific answer ready for this topic, "
        "here are some ways I can help:\n\n"
        "**Try asking me about:**\n"
        "• How to get free legal aid (NALSA)\n"
        "• How to file an FIR\n"
        "• Your rights if arrested\n"
        "• Filing a consumer court complaint\n"
        "• Key changes in Bharatiya Nyaya Sanhita (BNS)\n"
        "• Fundamental Rights under the Constitution\n"
        "• RTI (Right to Information)\n"
        "• Cyber crime reporting\n"
        "• Divorce and maintenance laws\n"
        "• Property and inheritance rights\n"
        "• Traffic laws and e-challan\n"
        "• Labour and employment rights\n\n"
        "For specific legal advice, please visit our **Find Lawyers** section to connect with a qualified legal professional."
    )


SYSTEM_INSTRUCTION = """
You are the Nyaysetu AI Assistant, a friendly, professional, and accessible legal guide for the Nyaysetu website.
Your primary role is to help users navigate the website and answer basic legal FAQs accurately according to Indian law.

Key responsibilities:
1. Guide users through the platform features (Analyze Documents, Find Lawyers, Case Tracking, Legal Knowledge).
2. Answer frequently asked legal questions simply and clearly, referencing official Indian legal sources (like NALSA, the Constitution, BNS, IPC, BNSS, BSA) when applicable.
3. Keep your answers concise, accessible to laypersons, and highly accurate. Do NOT hallucinate laws.
4. If a user asks for formal legal advice, remind them that you provide legal information, not formal legal counsel, and direct them to the "Find Lawyers" section.
5. Provide your answers in standard Markdown format (using bolding, bullets, and short paragraphs) so it renders well in the chat UI.
6. Always cite the specific section number and act name when referencing any law.
"""


@router.post("/chat", response_model=ChatResponse)
async def bot_chat(request: ChatRequest):
    # First, try the built-in FAQ database for instant, reliable answers
    faq_answer = _find_faq_answer(request.message)

    # Try Gemini API if available
    api_key = os.environ.get("GEMINI_API_KEY")
    has_valid_key = api_key and api_key != "your_api_key_here" and len(api_key) > 20

    if has_valid_key:
        try:
            client = genai.Client(api_key=api_key)

            # Convert history into the format expected by the Google GenAI SDK
            contents = []
            for msg in request.history:
                role = "user" if msg.role == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))

            # Add the new message
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,
                ),
            )

            return ChatResponse(status="success", reply=response.text)

        except Exception as e:
            # Gemini API failed — fall back to FAQ or generic response
            print(f"[Nyaysetu Bot] Gemini API error: {e}")

    # If Gemini is not available, use FAQ or generic response
    if faq_answer:
        return ChatResponse(status="success", reply=faq_answer)
    else:
        return ChatResponse(status="success", reply=_get_generic_response())
