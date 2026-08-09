"""
Curated corpus of Indian legal provisions.

Every passage carries the act, the section and a verifiable source, because a
legal answer without a citation is worse than no answer — the reader cannot
check it, and a wrong forum or a missed limitation period has real cost.

Passages are written in plain language rather than quoted verbatim from the
bare acts: the audience is a person trying to solve a problem, not a lawyer
reading a commentary. Where a provision is commonly known by its old number
(the 2023 criminal codes renumbered nearly everything), the former reference is
kept in `also_known_as` so a search for "Section 154 CrPC" still lands.

Keep this file the single source of truth. The retriever indexes whatever is
here; adding a passage is all that is needed to teach the assistant a topic.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Passage:
    id: str
    title: str
    act: str
    section: str
    text: str
    source_url: str
    topics: tuple[str, ...] = ()
    #: Former or colloquial references that should still match this passage.
    also_known_as: tuple[str, ...] = ()

    @property
    def citation(self) -> str:
        return f"{self.act} — {self.section}" if self.section else self.act


INDIA_CODE = "https://www.indiacode.nic.in"

CORPUS: list[Passage] = [
    # ── Access to justice ───────────────────────────────────────────────
    Passage(
        id="legal_aid_eligibility",
        title="Who can get free legal aid",
        act="Legal Services Authorities Act, 1987",
        section="Section 12",
        text=(
            "Free legal aid is a statutory right, not charity. You are entitled to a lawyer "
            "at State expense if you fall into any of these categories: a member of a Scheduled "
            "Caste or Scheduled Tribe; a victim of trafficking or begar (forced labour); a woman "
            "or a child; a person with a disability; a victim of mass disaster, ethnic violence, "
            "caste atrocity, flood, drought, earthquake or industrial disaster; an industrial "
            "workman; a person in custody, including in a protective home or juvenile home; or a "
            "person whose annual income falls below the limit set by the State (commonly around "
            "three lakh rupees, and higher for Supreme Court matters). "
            "Note that a person in custody qualifies regardless of income, and so does any woman "
            "or child regardless of income."
        ),
        source_url="https://nalsa.gov.in",
        topics=("legal aid", "nalsa", "free lawyer", "poverty", "access to justice"),
    ),
    Passage(
        id="legal_aid_how_to_apply",
        title="How to actually apply for free legal aid",
        act="Legal Services Authorities Act, 1987",
        section="Sections 9–12",
        text=(
            "Apply at the District Legal Services Authority (DLSA) located in your district court "
            "complex. You can walk in and fill a simple form; no lawyer is needed to apply. "
            "Alternatively apply online at nalsa.gov.in, or call the national legal aid helpline "
            "on 15100. Every state also runs Legal Aid Clinics at the taluka level and inside "
            "prisons. If your matter is already before a court, you can ask that court directly "
            "to appoint legal aid counsel. There is no fee at any stage."
        ),
        source_url="https://nalsa.gov.in",
        topics=("legal aid", "nalsa", "dlsa", "helpline", "how to apply"),
    ),
    Passage(
        id="lok_adalat",
        title="Lok Adalat — settling a case without trial",
        act="Legal Services Authorities Act, 1987",
        section="Sections 19–22",
        text=(
            "A Lok Adalat settles disputes by compromise. Its award has the same force as a civil "
            "court decree and cannot be appealed, so it ends the matter for good. Court fees "
            "already paid are refunded when a case settles there. It handles compoundable criminal "
            "cases, motor accident claims, matrimonial disputes, bank recovery, and utility bills, "
            "but not non-compoundable offences. National Lok Adalats are held on scheduled dates "
            "several times a year. Because both sides must agree, nothing is imposed on you."
        ),
        source_url="https://nalsa.gov.in",
        topics=("lok adalat", "settlement", "compromise", "mediation", "court fee"),
    ),

    # ── Police, FIR, arrest ─────────────────────────────────────────────
    Passage(
        id="fir_how_to_file",
        title="How to file an FIR",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 173",
        text=(
            "An FIR (First Information Report) records information about a cognizable offence. "
            "Go to the police station with jurisdiction over the place the offence happened, and "
            "give the information orally or in writing. If given orally, the officer must write it "
            "down and read it back to you, and you sign it. "
            "You are entitled to a free copy of the FIR — this is not a favour and you should not "
            "leave without it. Since the 2023 code, information about a cognizable offence may "
            "also be given electronically, and by any person, not only the victim."
        ),
        source_url=INDIA_CODE,
        topics=("fir", "police", "complaint", "cognizable offence"),
        also_known_as=("Section 154 CrPC", "154 CrPC"),
    ),
    Passage(
        id="zero_fir",
        title="Zero FIR — when the police say it is not their area",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 173(1)",
        text=(
            "A police station cannot refuse to register an FIR on the ground that the offence "
            "happened somewhere else. It must register a Zero FIR and transfer it to the station "
            "with jurisdiction. This matters most in sexual offence and urgent cases, where "
            "sending a victim across the city to another station causes real harm. "
            "If an officer refuses, note their name and buckle number and escalate immediately."
        ),
        source_url=INDIA_CODE,
        topics=("zero fir", "jurisdiction", "police refusal", "fir"),
    ),
    Passage(
        id="fir_refusal_remedy",
        title="What to do if the police refuse to register your FIR",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Sections 173(4) and 175(3)",
        text=(
            "You have an escalating set of remedies. First, send the complaint in writing by "
            "registered post to the Superintendent of Police; if satisfied a cognizable offence is "
            "disclosed, the SP must investigate or direct an investigation. If that also fails, "
            "apply to the Judicial Magistrate, who can direct the police to investigate. "
            "Refusal to record information about certain offences — including offences against "
            "women — is itself a punishable offence for the officer. "
            "Keep proof of posting; it establishes the date you tried."
        ),
        source_url=INDIA_CODE,
        topics=("fir refused", "police complaint", "magistrate", "superintendent of police"),
        also_known_as=("Section 156(3) CrPC", "156(3)"),
    ),
    Passage(
        id="arrest_rights",
        title="Your rights when you are arrested",
        act="Constitution of India and Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Articles 20–22; BNSS Sections 47 and 58",
        text=(
            "You must be told the grounds of your arrest — the police cannot simply take you away. "
            "You have the right to consult and be defended by a lawyer of your choice, and to free "
            "legal aid if you cannot afford one. You must be produced before a Magistrate within "
            "twenty-four hours, excluding travel time; detention beyond that without a Magistrate's "
            "authorisation is illegal. You cannot be compelled to be a witness against yourself. "
            "A relative or nominated person must be informed of your arrest and where you are held. "
            "You have a right to be examined by a medical practitioner. "
            "Handcuffing is restricted and is not routine."
        ),
        source_url=INDIA_CODE,
        topics=("arrest", "police custody", "rights", "detention", "24 hours"),
        also_known_as=("Section 50 CrPC", "Section 57 CrPC"),
    ),
    Passage(
        id="dk_basu",
        title="D.K. Basu guidelines on arrest and custody",
        act="D.K. Basu v. State of West Bengal",
        section="(1997) 1 SCC 416",
        text=(
            "The Supreme Court laid down binding requirements for every arrest. Police must wear "
            "accurate, visible identification; prepare a memo of arrest attested by a witness (a "
            "family member or a respectable local person) and countersigned by the arrestee with "
            "the time and date; inform a friend or relative of the arrest and place of detention; "
            "record the arrest in a diary; and conduct a medical examination every forty-eight "
            "hours during custody. Failure to comply is contempt of court and departmental "
            "misconduct. These guidelines have since been substantially written into statute."
        ),
        source_url="https://main.sci.gov.in",
        topics=("arrest", "custody", "police", "torture", "landmark judgment", "guidelines"),
    ),
    Passage(
        id="anticipatory_bail",
        title="Anticipatory bail — protection before arrest",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 482",
        text=(
            "If you have reason to believe you may be arrested for a non-bailable offence, you can "
            "apply to the Sessions Court or the High Court for a direction that you be released on "
            "bail in the event of arrest. The court weighs the nature and gravity of the "
            "accusation, your antecedents, and whether the accusation appears aimed at humiliating "
            "you. Conditions are usually imposed, such as making yourself available for "
            "interrogation and not tampering with evidence."
        ),
        source_url=INDIA_CODE,
        topics=("anticipatory bail", "bail", "arrest", "non-bailable"),
        also_known_as=("Section 438 CrPC", "438 CrPC"),
    ),
    Passage(
        id="bail_default",
        title="Default bail when the investigation drags on",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 187",
        text=(
            "If the police do not complete the investigation and file a charge sheet within the "
            "prescribed period, you become entitled to be released on bail — this is called default "
            "or statutory bail. The period is ninety days for offences punishable with death, life "
            "imprisonment, or imprisonment of ten years or more, and sixty days for other offences. "
            "The right must be claimed while it subsists; it is lost once the charge sheet is filed. "
            "Apply the moment the period expires."
        ),
        source_url=INDIA_CODE,
        topics=("default bail", "statutory bail", "charge sheet", "90 days", "60 days"),
        also_known_as=("Section 167 CrPC", "167(2) CrPC"),
    ),

    # ── The 2023 criminal codes ─────────────────────────────────────────
    Passage(
        id="bns_overview",
        title="Bharatiya Nyaya Sanhita — what replaced the Indian Penal Code",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Act 45 of 2023",
        text=(
            "The BNS replaced the Indian Penal Code, 1860 with effect from 1 July 2024, reducing "
            "511 sections to 358. Sedition as it existed under Section 124A IPC was repealed. "
            "Community service was introduced as a punishment for certain petty offences. "
            "Offences against women and children were grouped into a dedicated chapter and given "
            "priority. Organised crime, terrorism, mob lynching and snatching were defined in the "
            "general penal code for the first time. "
            "Offences committed before 1 July 2024 continue to be tried under the IPC, so the old "
            "code still matters for pending cases."
        ),
        source_url=INDIA_CODE,
        topics=("bns", "ipc", "new criminal law", "2023", "penal code"),
    ),
    Passage(
        id="bnss_overview",
        title="Bharatiya Nagarik Suraksha Sanhita — what replaced the CrPC",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Act 46 of 2023",
        text=(
            "The BNSS replaced the Code of Criminal Procedure, 1973 from 1 July 2024. It introduces "
            "timelines intended to speed up cases: judgment within forty-five days of the end of "
            "trial, charges framed within sixty days of the first hearing. It provides for Zero FIR, "
            "electronic filing of information, and mandatory forensic investigation for offences "
            "punishable with seven years or more. Videography of search and seizure is required. "
            "Trial in absentia of proclaimed offenders is permitted in defined circumstances."
        ),
        source_url=INDIA_CODE,
        topics=("bnss", "crpc", "criminal procedure", "2023"),
    ),
    Passage(
        id="bsa_overview",
        title="Bharatiya Sakshya Adhiniyam — the new evidence law",
        act="Bharatiya Sakshya Adhiniyam, 2023",
        section="Act 47 of 2023",
        text=(
            "The BSA replaced the Indian Evidence Act, 1872 from 1 July 2024. Its most significant "
            "change is placing electronic and digital records on the same footing as primary "
            "documentary evidence, with defined requirements for authentication. This covers "
            "records on semiconductor memory, smartphones, servers and cloud storage. "
            "Oral evidence may be given electronically, which allows remote testimony."
        ),
        source_url=INDIA_CODE,
        topics=("bsa", "evidence act", "digital evidence", "electronic records"),
    ),
    Passage(
        id="bns_sedition_replacement",
        title="Sedition repealed, and what replaced it",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Section 152",
        text=(
            "The offence of sedition under Section 124A of the Indian Penal Code has been repealed. "
            "Section 152 BNS creates a distinct offence of acts endangering the sovereignty, unity "
            "and integrity of India — covering the excitement of secession, armed rebellion or "
            "subversive activities, including by electronic communication or financial means. "
            "The offence carries life imprisonment or up to seven years. Commentators differ on "
            "whether the new provision is genuinely narrower in practice; the Supreme Court had "
            "separately kept Section 124A in abeyance in 2022."
        ),
        source_url=INDIA_CODE,
        topics=("sedition", "124a", "section 152", "free speech"),
    ),
    Passage(
        id="bns_mob_lynching",
        title="Mob lynching as a distinct offence",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Section 103(2)",
        text=(
            "Where a group of five or more persons acting together commits murder on the ground of "
            "race, caste or community, sex, place of birth, language, personal belief or any similar "
            "ground, each member of the group is punishable with death or life imprisonment, and "
            "also a fine. This gives mob lynching a specific statutory identity for the first time; "
            "previously such cases were prosecuted under general murder and unlawful assembly "
            "provisions."
        ),
        source_url=INDIA_CODE,
        topics=("mob lynching", "hate crime", "murder", "section 103"),
    ),
    Passage(
        id="bns_cruelty_husband",
        title="Cruelty by a husband or his relatives",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Section 85",
        text=(
            "A husband or a relative of a husband who subjects a woman to cruelty is punishable "
            "with imprisonment up to three years and a fine. Cruelty covers wilful conduct likely "
            "to drive the woman to suicide or to cause grave injury or danger to her life, limb or "
            "health — mental as well as physical — and also harassment aimed at coercing her or her "
            "relatives to meet an unlawful demand for property or valuable security. "
            "This carries forward what was Section 498A of the Indian Penal Code."
        ),
        source_url=INDIA_CODE,
        topics=("cruelty", "498a", "domestic", "dowry harassment", "women"),
        also_known_as=("Section 498A IPC", "498A"),
    ),
    Passage(
        id="bns_dowry_death",
        title="Dowry death",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Section 80",
        text=(
            "Where a woman dies of burns, bodily injury or otherwise than under normal circumstances "
            "within seven years of marriage, and it is shown that shortly before her death she was "
            "subjected to cruelty or harassment by her husband or his relative in connection with a "
            "demand for dowry, the death is treated as a dowry death and the husband or relative is "
            "deemed to have caused it. Punishment is imprisonment of not less than seven years, "
            "extending to life."
        ),
        source_url=INDIA_CODE,
        topics=("dowry death", "dowry", "women", "section 304b"),
        also_known_as=("Section 304B IPC",),
    ),
    Passage(
        id="bns_stalking",
        title="Stalking, including online stalking",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Section 78",
        text=(
            "A man who follows a woman and contacts, or attempts to contact, her to foster personal "
            "interaction repeatedly despite a clear indication of disinterest commits stalking. "
            "Monitoring a woman's use of the internet, email or any other form of electronic "
            "communication is expressly covered. First conviction carries up to three years and a "
            "fine; a subsequent conviction up to five years. The offence is cognizable."
        ),
        source_url=INDIA_CODE,
        topics=("stalking", "cyber stalking", "harassment", "women", "online"),
        also_known_as=("Section 354D IPC",),
    ),
    Passage(
        id="bns_hit_and_run",
        title="Causing death by negligence and hit-and-run",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Section 106",
        text=(
            "Causing death by a rash or negligent act not amounting to culpable homicide is "
            "punishable with imprisonment up to five years and a fine. Where the person causing "
            "death by rash or negligent driving escapes without reporting the incident to a police "
            "officer or Magistrate soon after, the punishment extends to ten years. "
            "A registered medical practitioner causing death by a negligent medical act faces a "
            "lower maximum of two years."
        ),
        source_url=INDIA_CODE,
        topics=("hit and run", "negligence", "accident", "driving", "death"),
        also_known_as=("Section 304A IPC",),
    ),

    # ── Constitution ────────────────────────────────────────────────────
    Passage(
        id="fundamental_rights",
        title="Fundamental Rights in brief",
        act="Constitution of India",
        section="Part III, Articles 12–35",
        text=(
            "Part III guarantees six groups of rights enforceable against the State. "
            "Right to Equality (Articles 14–18) covers equality before law, non-discrimination on "
            "grounds of religion, race, caste, sex or place of birth, equality of opportunity in "
            "public employment, and abolition of untouchability. "
            "Right to Freedom (Articles 19–22) covers speech and expression, assembly, association, "
            "movement, residence and profession, protection in respect of conviction, life and "
            "personal liberty, and protection against arbitrary arrest. "
            "Right against Exploitation (Articles 23–24) prohibits trafficking, forced labour and "
            "child labour in hazardous work. "
            "Right to Freedom of Religion (Articles 25–28). "
            "Cultural and Educational Rights (Articles 29–30). "
            "Right to Constitutional Remedies (Article 32)."
        ),
        source_url="https://legislative.gov.in",
        topics=("fundamental rights", "constitution", "part iii", "equality", "freedom"),
    ),
    Passage(
        id="article_21",
        title="Article 21 — life and personal liberty",
        act="Constitution of India",
        section="Article 21",
        text=(
            "No person shall be deprived of his life or personal liberty except according to "
            "procedure established by law. Following Maneka Gandhi, that procedure must itself be "
            "just, fair and reasonable, not arbitrary or oppressive. The courts have read into "
            "Article 21 the right to live with dignity, to livelihood, to health and medical care, "
            "to a clean environment, to shelter, to a speedy trial, to legal aid, to privacy, and "
            "to die with dignity in the limited sense of passive euthanasia. "
            "Article 21 is available to every person, not only citizens."
        ),
        source_url="https://legislative.gov.in",
        topics=("article 21", "right to life", "liberty", "dignity", "constitution"),
    ),
    Passage(
        id="article_32",
        title="Article 32 and the five writs",
        act="Constitution of India",
        section="Article 32 (and Article 226)",
        text=(
            "Article 32 lets you move the Supreme Court directly to enforce a Fundamental Right; "
            "Ambedkar called it the heart and soul of the Constitution. High Courts have wider "
            "power under Article 226, which covers both Fundamental Rights and other legal rights. "
            "The five writs are: habeas corpus, to produce a person unlawfully detained; mandamus, "
            "to compel a public authority to perform its duty; prohibition, to stop a lower court "
            "exceeding its jurisdiction; certiorari, to quash an order already passed without "
            "jurisdiction; and quo warranto, to question a person's holding of a public office. "
            "In practice, going to the High Court under Article 226 first is often the better route."
        ),
        source_url="https://legislative.gov.in",
        topics=("article 32", "writ", "habeas corpus", "mandamus", "supreme court", "high court"),
    ),
    Passage(
        id="kesavananda",
        title="Basic structure doctrine",
        act="Kesavananda Bharati v. State of Kerala",
        section="(1973) 4 SCC 225",
        text=(
            "A thirteen-judge bench held that Parliament's power to amend the Constitution under "
            "Article 368 is wide but not unlimited: it cannot alter or destroy the basic structure. "
            "Features identified over time as part of that structure include supremacy of the "
            "Constitution, the rule of law, separation of powers, judicial review, federalism, "
            "secularism, free and fair elections, and the independence of the judiciary. "
            "This is the doctrine that allows courts to strike down a constitutional amendment."
        ),
        source_url="https://main.sci.gov.in",
        topics=("kesavananda", "basic structure", "amendment", "article 368", "landmark judgment"),
    ),
    Passage(
        id="puttaswamy",
        title="Right to privacy as a fundamental right",
        act="Justice K.S. Puttaswamy (Retd.) v. Union of India",
        section="(2017) 10 SCC 1",
        text=(
            "A nine-judge bench unanimously held that the right to privacy is protected as an "
            "intrinsic part of the right to life and personal liberty under Article 21 and of the "
            "freedoms in Part III. Any State intrusion must satisfy a threefold test: it must be "
            "backed by law, pursue a legitimate State aim, and be proportionate to that aim. "
            "The judgment underpins India's data protection framework and informed later decisions "
            "on decriminalising consensual same-sex relations and on Aadhaar."
        ),
        source_url="https://main.sci.gov.in",
        topics=("privacy", "puttaswamy", "aadhaar", "data protection", "article 21"),
    ),
    Passage(
        id="maneka_gandhi",
        title="Due process read into Article 21",
        act="Maneka Gandhi v. Union of India",
        section="(1978) 1 SCC 248",
        text=(
            "The Supreme Court held that a law depriving a person of personal liberty must lay down "
            "a procedure that is right, just and fair, and not arbitrary or oppressive. It linked "
            "Articles 14, 19 and 21 — the golden triangle — so that a law restricting liberty must "
            "also satisfy the tests of equality and reasonableness. The case arose from the "
            "impounding of a passport without reasons, and expanded Article 21 far beyond its "
            "earlier narrow reading."
        ),
        source_url="https://main.sci.gov.in",
        topics=("maneka gandhi", "article 21", "due process", "golden triangle", "landmark judgment"),
    ),
    Passage(
        id="vishaka_posh",
        title="Sexual harassment at the workplace",
        act="Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013",
        section="Sections 4, 9 and 11",
        text=(
            "Every employer with ten or more employees must constitute an Internal Committee, "
            "headed by a woman, with at least half its members women and one member from an NGO "
            "familiar with the issues. A complaint should ordinarily be made within three months of "
            "the incident, extendable by a further three months for recorded reasons. The Committee "
            "must complete its inquiry within ninety days. Where there is no Internal Committee, or "
            "the complaint is against the employer, it goes to the Local Committee constituted by "
            "the District Officer. The Act grew out of the Vishaka guidelines laid down by the "
            "Supreme Court in 1997 in the absence of legislation."
        ),
        source_url=INDIA_CODE,
        topics=("posh", "sexual harassment", "workplace", "vishaka", "internal committee", "women"),
    ),

    # ── Consumer ────────────────────────────────────────────────────────
    Passage(
        id="consumer_where_to_file",
        title="Where to file a consumer complaint",
        act="Consumer Protection Act, 2019",
        section="Sections 34, 47 and 58",
        text=(
            "Jurisdiction depends on the value of the goods or services paid as consideration, not "
            "on the compensation claimed. Up to fifty lakh rupees goes to the District Commission; "
            "above fifty lakh and up to two crore to the State Commission; above two crore to the "
            "National Commission. "
            "You may file where you actually reside or work, which was a significant improvement "
            "over the old law. The limitation period is two years from the date the cause of action "
            "arose. You do not need a lawyer and can argue the case yourself."
        ),
        source_url="https://consumerhelpline.gov.in",
        topics=("consumer", "complaint", "jurisdiction", "district commission", "refund"),
    ),
    Passage(
        id="consumer_how_to_file",
        title="How to file a consumer complaint",
        act="Consumer Protection Act, 2019",
        section="Section 35",
        text=(
            "Send a written legal notice to the seller or service provider first, giving them a "
            "chance to remedy the defect; keep proof of dispatch. Then file online at edaakhil.nic.in "
            "or in person at the Commission. Attach the invoice, warranty card, payment proof, and "
            "all correspondence. Court fees are nominal and are waived for claims up to five lakh "
            "rupees. You can also register a grievance on the National Consumer Helpline at 1915 "
            "or on the NCH app, which often resolves matters without litigation."
        ),
        source_url="https://edaakhil.nic.in",
        topics=("consumer", "edaakhil", "helpline 1915", "how to file", "legal notice"),
    ),
    Passage(
        id="consumer_unfair_practice",
        title="Unfair trade practices and misleading advertisements",
        act="Consumer Protection Act, 2019",
        section="Sections 2(47) and 21",
        text=(
            "Unfair trade practice covers false representation about quality or standard, "
            "misleading warranties, bargain pricing that is not genuine, and refusing to take back "
            "or withdraw defective goods. The Central Consumer Protection Authority can order a "
            "misleading advertisement discontinued and impose a penalty on the manufacturer or "
            "endorser — up to ten lakh rupees, and up to fifty lakh for repeat offences. "
            "Endorsers, including celebrities, can be barred from making endorsements for a period."
        ),
        source_url="https://consumerhelpline.gov.in",
        topics=("unfair trade practice", "misleading advertisement", "ccpa", "consumer"),
    ),

    # ── Transparency ────────────────────────────────────────────────────
    Passage(
        id="rti_how_to_file",
        title="How to file an RTI application",
        act="Right to Information Act, 2005",
        section="Sections 6 and 7",
        text=(
            "Write a plain application to the Public Information Officer of the concerned public "
            "authority. You do not need to give a reason for wanting the information, and you "
            "cannot be asked for one. The fee is ten rupees, payable by cash, demand draft, "
            "postal order or online; applicants below the poverty line pay nothing. "
            "For Central Government bodies, file online at rtionline.gov.in. States have their own "
            "portals. Information must be supplied within thirty days, or within forty-eight hours "
            "where it concerns the life or liberty of a person."
        ),
        source_url="https://rtionline.gov.in",
        topics=("rti", "right to information", "pio", "transparency", "government"),
    ),
    Passage(
        id="rti_appeals",
        title="RTI appeals and penalties for delay",
        act="Right to Information Act, 2005",
        section="Sections 19 and 20",
        text=(
            "If the information is refused, incomplete, or not supplied in time, file a first "
            "appeal with the First Appellate Authority in the same department within thirty days. "
            "If still unsatisfied, file a second appeal with the Central or State Information "
            "Commission within ninety days. "
            "A Public Information Officer who refuses without reasonable cause, delays, or gives "
            "false or incomplete information is liable to a penalty of two hundred and fifty rupees "
            "per day, up to twenty-five thousand rupees, plus disciplinary action. "
            "There is no fee for either appeal."
        ),
        source_url="https://cic.gov.in",
        topics=("rti appeal", "information commission", "penalty", "delay"),
    ),

    # ── Cyber ───────────────────────────────────────────────────────────
    Passage(
        id="cybercrime_reporting",
        title="Reporting a cybercrime or online fraud",
        act="Information Technology Act, 2000 and Bharatiya Nyaya Sanhita, 2023",
        section="IT Act Sections 66, 66C, 66D, 67",
        text=(
            "Report at cybercrime.gov.in or call 1930, the national cyber fraud helpline. "
            "For financial fraud, speed is everything: reporting within the first few hours gives "
            "the best chance of freezing the money before it is withdrawn, through the Citizen "
            "Financial Cyber Fraud Reporting and Management System. "
            "Preserve evidence — screenshots showing URLs and timestamps, transaction reference "
            "numbers, the sender's number or email headers. Do not delete the messages. "
            "Common offences include hacking, identity theft, cheating by personation using a "
            "computer resource, and publishing obscene material electronically."
        ),
        source_url="https://cybercrime.gov.in",
        topics=("cyber crime", "online fraud", "hacking", "1930", "phishing", "upi fraud"),
    ),
    Passage(
        id="obscene_content_online",
        title="Non-consensual intimate images and obscene content online",
        act="Information Technology Act, 2000",
        section="Sections 66E, 67, 67A",
        text=(
            "Capturing, publishing or transmitting the image of a private area of a person without "
            "consent is punishable with up to three years or a fine up to two lakh rupees. "
            "Publishing obscene material in electronic form carries up to three years and a fine on "
            "first conviction; sexually explicit material carries up to five years. "
            "Report at cybercrime.gov.in, which has a dedicated channel for reporting crimes against "
            "women and children that permits anonymous reporting. Intermediaries are obliged to "
            "remove such content expeditiously once notified."
        ),
        source_url="https://cybercrime.gov.in",
        topics=("revenge porn", "obscene", "privacy", "intimate images", "takedown", "women"),
    ),

    # ── Family ──────────────────────────────────────────────────────────
    Passage(
        id="divorce_grounds_hindu",
        title="Grounds for divorce under the Hindu Marriage Act",
        act="Hindu Marriage Act, 1955",
        section="Section 13",
        text=(
            "Either spouse may petition on the grounds of adultery, cruelty, desertion for at least "
            "two continuous years, conversion to another religion, incurable unsoundness of mind or "
            "mental disorder, virulent and incurable leprosy (since amended), venereal disease in a "
            "communicable form, renunciation of the world, or not having been heard of as alive for "
            "seven years. A wife has additional grounds, including bigamy by the husband and a "
            "decree for maintenance where cohabitation has not resumed for a year. "
            "The Act governs Hindus, Buddhists, Jains and Sikhs."
        ),
        source_url=INDIA_CODE,
        topics=("divorce", "hindu marriage act", "cruelty", "desertion", "grounds"),
    ),
    Passage(
        id="divorce_mutual_consent",
        title="Divorce by mutual consent",
        act="Hindu Marriage Act, 1955",
        section="Section 13B",
        text=(
            "Both spouses may jointly petition on the ground that they have been living separately "
            "for a year or more and have agreed the marriage should be dissolved. A second motion "
            "must be made after six months and within eighteen months of the first. "
            "The Supreme Court held in Amardeep Singh v. Harveen Kaur (2017) that the six-month "
            "period is directory, not mandatory, and can be waived where the separation has already "
            "exceeded the statutory period and all issues including alimony and custody are settled. "
            "The Court has also used Article 142 to dissolve marriages that have irretrievably "
            "broken down."
        ),
        source_url=INDIA_CODE,
        topics=("mutual consent divorce", "13b", "cooling off", "waiver", "amardeep singh"),
    ),
    Passage(
        id="maintenance",
        title="Maintenance for wife, children and parents",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 144",
        text=(
            "A person with sufficient means who neglects or refuses to maintain a wife unable to "
            "maintain herself, a legitimate or illegitimate minor child, a child unable to maintain "
            "itself by reason of physical or mental abnormality, or a father or mother unable to "
            "maintain themselves, may be ordered by a Magistrate to pay a monthly allowance. "
            "This remedy is secular — it applies regardless of religion, which is what the Shah Bano "
            "case established. It is summary and comparatively quick, and a divorced wife who has "
            "not remarried is included."
        ),
        source_url=INDIA_CODE,
        topics=("maintenance", "alimony", "wife", "parents", "children", "125 crpc"),
        also_known_as=("Section 125 CrPC", "125 CrPC"),
    ),
    Passage(
        id="domestic_violence",
        title="Protection from domestic violence",
        act="Protection of Women from Domestic Violence Act, 2005",
        section="Sections 3, 12, 17 and 18",
        text=(
            "Domestic violence covers physical, sexual, verbal, emotional and economic abuse within "
            "a domestic relationship. The Act is civil in nature, and available to a wife, a female "
            "partner in a relationship in the nature of marriage, a mother, a sister or any woman "
            "in a shared household. "
            "You can seek protection orders, residence orders (including the right to remain in the "
            "shared household regardless of who owns it), monetary relief, custody and compensation. "
            "Apply to the Magistrate through a Protection Officer, a service provider, or directly. "
            "The Magistrate should ordinarily dispose of the application within sixty days."
        ),
        source_url=INDIA_CODE,
        topics=("domestic violence", "pwdva", "protection order", "shared household", "women"),
    ),
    Passage(
        id="shah_bano",
        title="Maintenance regardless of religion",
        act="Mohd. Ahmed Khan v. Shah Bano Begum",
        section="(1985) 2 SCC 556",
        text=(
            "The Supreme Court held that a divorced Muslim woman unable to maintain herself is "
            "entitled to maintenance under the secular maintenance provision of the criminal "
            "procedure code, which applies to all citizens irrespective of personal law. "
            "The decision triggered the Muslim Women (Protection of Rights on Divorce) Act, 1986; "
            "the Supreme Court subsequently read that Act, in Danial Latifi (2001), as requiring "
            "reasonable and fair provision for the wife's future, and in 2024 confirmed that the "
            "secular remedy remains available to Muslim women."
        ),
        source_url="https://main.sci.gov.in",
        topics=("shah bano", "maintenance", "muslim women", "personal law", "landmark judgment"),
    ),

    # ── Property ────────────────────────────────────────────────────────
    Passage(
        id="daughters_coparcenary",
        title="Daughters' equal rights in ancestral property",
        act="Hindu Succession Act, 1956 (as amended in 2005)",
        section="Section 6",
        text=(
            "A daughter of a coparcener becomes a coparcener in her own right by birth, in the same "
            "manner as a son, with the same rights and liabilities in coparcenary property. "
            "In Vineeta Sharma v. Rakesh Sharma (2020), a three-judge bench held that this right "
            "arises by birth, so it does not matter whether the father was alive on the date of the "
            "2005 amendment. The right applies to Hindus, Buddhists, Jains and Sikhs. "
            "A daughter can demand partition and can also dispose of her share by will."
        ),
        source_url=INDIA_CODE,
        topics=("daughter property rights", "coparcener", "ancestral property", "succession", "vineeta sharma"),
    ),
    Passage(
        id="property_registration",
        title="Registering a property transfer",
        act="Registration Act, 1908 and Transfer of Property Act, 1882",
        section="Registration Act Section 17",
        text=(
            "Any instrument transferring immovable property worth more than one hundred rupees — "
            "which in practice means all of them — must be registered at the Sub-Registrar's office "
            "having jurisdiction over the property. An unregistered sale deed does not transfer "
            "title and cannot be received as evidence of the transaction. "
            "Registration must ordinarily be presented within four months of execution. "
            "Stamp duty is a State subject and rates differ; several States charge a lower rate "
            "where the buyer is a woman. An agreement to sell is not a sale deed and does not by "
            "itself transfer ownership."
        ),
        source_url=INDIA_CODE,
        topics=("property registration", "sale deed", "stamp duty", "sub registrar", "title"),
    ),
    Passage(
        id="senior_citizens_maintenance",
        title="Parents' right to maintenance and to reclaim property",
        act="Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        section="Sections 4, 5 and 23",
        text=(
            "A parent or grandparent unable to maintain themselves can apply to a Maintenance "
            "Tribunal, which is designed to work without lawyers and to decide within ninety days. "
            "Critically, where a senior citizen has transferred property to a child subject to the "
            "condition that the child provide basic amenities and physical needs, and the child "
            "fails to do so, the transfer may be declared void by the Tribunal at the senior "
            "citizen's option. Tribunals have used this to restore possession of homes."
        ),
        source_url=INDIA_CODE,
        topics=("senior citizens", "parents maintenance", "elder abuse", "property transfer void",
                "son refuses to look after me", "gave my house to my son", "abandoned by children",
                "old age", "neglected by son"),
    ),

    # ── Work ────────────────────────────────────────────────────────────
    Passage(
        id="labour_codes",
        title="The four labour codes",
        act="Code on Wages 2019; Industrial Relations Code 2020; Code on Social Security 2020; OSH Code 2020",
        section="Consolidation of 29 central labour laws",
        text=(
            "Parliament consolidated twenty-nine central labour laws into four codes: the Code on "
            "Wages (minimum wages, payment of wages, bonus, equal remuneration); the Industrial "
            "Relations Code (trade unions, standing orders, retrenchment, disputes); the Code on "
            "Social Security (provident fund, ESI, gratuity, maternity benefit, gig and platform "
            "workers); and the Occupational Safety, Health and Working Conditions Code. "
            "The codes were notified in 2025. Because labour is on the Concurrent List, "
            "State rules govern much of the day-to-day detail, so check your State's rules."
        ),
        source_url="https://labour.gov.in",
        topics=("labour codes", "employment", "wages", "trade union", "social security"),
    ),
    Passage(
        id="gratuity",
        title="Gratuity on leaving a job",
        act="Payment of Gratuity Act, 1972",
        section="Sections 4 and 7",
        text=(
            "Gratuity is payable on resignation, retirement or death to an employee who has "
            "completed five years of continuous service; the five-year condition does not apply "
            "where employment ends due to death or disablement. It is calculated as fifteen days' "
            "last drawn wages for every completed year of service, taking a month as twenty-six "
            "days. The statutory ceiling is twenty lakh rupees. "
            "The employer must pay within thirty days of it becoming due, and owes simple interest "
            "for delay. Apply in Form I to the employer; if refused, apply to the Controlling "
            "Authority under the Act."
        ),
        source_url=INDIA_CODE,
        topics=("gratuity", "resignation", "retirement", "five years", "employment"),
    ),
    Passage(
        id="maternity_benefit",
        title="Maternity leave and benefits",
        act="Maternity Benefit Act, 1961 (amended 2017)",
        section="Sections 5, 5A, 11A and 12",
        text=(
            "A woman who has worked at least eighty days in the twelve months before her expected "
            "delivery is entitled to twenty-six weeks of paid maternity leave for her first two "
            "children, of which not more than eight weeks may be taken before delivery; twelve weeks "
            "for a third or subsequent child. A commissioning mother and a mother adopting a child "
            "below three months are entitled to twelve weeks. "
            "Establishments with fifty or more employees must provide a creche. "
            "Dismissal or notice during maternity leave is prohibited, and the employer must allow "
            "nursing breaks after return."
        ),
        source_url=INDIA_CODE,
        topics=("maternity leave", "26 weeks", "pregnancy", "women", "employment", "creche"),
    ),

    # ── Everyday ────────────────────────────────────────────────────────
    Passage(
        id="traffic_penalties",
        title="Traffic offences and e-challan",
        act="Motor Vehicles Act, 1988 (amended 2019)",
        section="Chapter XIII",
        text=(
            "The 2019 amendment raised penalties sharply. Indicative central figures: driving "
            "without a licence five thousand rupees; driving without insurance two thousand for a "
            "first offence; drunk driving ten thousand or imprisonment; over-speeding one to two "
            "thousand depending on vehicle class; using a mobile phone while driving five thousand; "
            "not wearing a seat belt or helmet one thousand. Where a minor drives, the guardian or "
            "vehicle owner may face up to three years' imprisonment and a twenty-five thousand rupee "
            "fine, and the vehicle's registration may be cancelled. "
            "States may notify lower amounts, so local figures vary. Check and pay pending challans "
            "at echallan.parivahan.gov.in."
        ),
        source_url="https://echallan.parivahan.gov.in",
        topics=("traffic", "challan", "driving", "motor vehicle", "fine", "helmet"),
    ),
    Passage(
        id="cheque_bounce",
        title="Cheque bounce",
        act="Negotiable Instruments Act, 1881",
        section="Section 138",
        text=(
            "Dishonour of a cheque for insufficiency of funds is an offence punishable with "
            "imprisonment up to two years, or a fine up to twice the cheque amount, or both. "
            "The timeline is strict and missing a step is fatal to the case. The cheque must be "
            "presented within three months of its date. On dishonour, send a written demand notice "
            "within thirty days of receiving the bank's memo. The drawer then has fifteen days to "
            "pay. If they do not, file a complaint before a Magistrate within one month of that "
            "fifteen-day period expiring. "
            "Courts may order interim compensation of up to twenty per cent of the cheque amount."
        ),
        source_url=INDIA_CODE,
        topics=("cheque bounce", "section 138", "dishonour", "demand notice", "recovery"),
    ),
    Passage(
        id="tenant_rights",
        title="Rent, deposit and eviction",
        act="Model Tenancy Act, 2021 and State Rent Acts",
        section="Model Act Sections 4, 11 and 21",
        text=(
            "Tenancy is a State subject, so your rights depend on the State's rent legislation; the "
            "Model Tenancy Act, 2021 is a template States may adopt, and several have. "
            "Under the Model Act, every tenancy requires a written agreement filed with the Rent "
            "Authority. The security deposit is capped at two months' rent for residential premises. "
            "A landlord must give twenty-four hours' notice before entering. "
            "A landlord cannot cut off essential supplies such as water and electricity, and cannot "
            "evict without an order of the Rent Court. Where a tenant refuses to vacate after the "
            "tenancy ends, enhanced rent becomes payable."
        ),
        source_url=INDIA_CODE,
        topics=("rent", "tenant", "landlord", "eviction", "security deposit"),
    ),
    Passage(
        id="sc_st_atrocities",
        title="Protection against caste atrocities",
        act="Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        section="Sections 3, 4, 15A and 18",
        text=(
            "The Act creates specific offences of atrocity against members of Scheduled Castes and "
            "Scheduled Tribes, including social and economic boycott, wrongful occupation of land, "
            "and caste-based insult in public view. Public servants who wilfully neglect their "
            "duties under the Act are themselves punishable. "
            "Anticipatory bail is barred. Special Courts conduct trials, which should be completed "
            "within two months of the charge sheet. Victims and witnesses have statutory rights, "
            "including travelling and maintenance expenses and protection, and relief is payable "
            "at defined stages of the case."
        ),
        source_url=INDIA_CODE,
        topics=("sc st act", "caste", "atrocity", "discrimination", "special court"),
    ),
    Passage(
        id="pocso",
        title="Sexual offences against children",
        act="Protection of Children from Sexual Offences Act, 2012",
        section="Sections 19, 21 and 33",
        text=(
            "The Act is gender-neutral and covers anyone below eighteen. Reporting is mandatory: "
            "a person who fails to report an offence they know of is themselves liable, with an "
            "exemption for the child. Report to the Special Juvenile Police Unit, the local police, "
            "or on the childline number 1098. "
            "The child's statement is recorded at their residence or a place of their choice, "
            "preferably by a woman officer not in uniform, and the child must not be called to the "
            "police station at night. The identity of the child may not be disclosed. "
            "Trials are held in Special Courts and are meant to conclude within one year."
        ),
        source_url=INDIA_CODE,
        topics=("pocso", "child abuse", "children", "1098", "mandatory reporting"),
    ),
    Passage(
        id="ration_food_security",
        title="Ration entitlement under food security law",
        act="National Food Security Act, 2013",
        section="Sections 3 and 10",
        text=(
            "Priority households are entitled to five kilograms of foodgrain per person per month, "
            "and Antyodaya Anna Yojana households to thirty-five kilograms per household per month, "
            "at subsidised prices from a fair price shop. Pregnant women and lactating mothers are "
            "entitled to maternity benefit of not less than six thousand rupees and to free meals. "
            "Children between six months and fourteen years are entitled to age-appropriate free "
            "meals. If your entitlement is denied, a District Grievance Redressal Officer is "
            "designated under the Act, and a food security allowance is payable for non-supply. "
            "One Nation One Ration Card allows the card to be used in any State."
        ),
        source_url=INDIA_CODE,
        topics=("ration card", "food security", "pds", "welfare", "grievance"),
    ),
]

# Second volume, split out only to keep each file readable. Imported at the
# bottom to avoid a circular import: corpus_extra needs Passage and INDIA_CODE
# from here.
from .corpus_extra import EXTRA_CORPUS  # noqa: E402

CORPUS.extend(EXTRA_CORPUS)

# Ids are used to pin retrieval from the UI, so a duplicate would silently
# shadow a passage. Fail loudly at import instead.
_seen: set[str] = set()
_duplicates = {p.id for p in CORPUS if p.id in _seen or _seen.add(p.id)}  # type: ignore[func-returns-value]
if _duplicates:
    raise RuntimeError(f"Duplicate passage ids in corpus: {sorted(_duplicates)}")

# Bulk passages ingested from public sources (see app/rag/ingest.py). Imported
# last and filtered against the ids above: where an ingested section collides
# with a hand-written passage, the hand-written one wins, because it was
# reviewed by a person and written for a reader rather than a lawyer.
from .store import load_all as _load_store  # noqa: E402

_ingested = [p for p in _load_store() if p.id not in _seen]
if _ingested:
    CORPUS.extend(_ingested)
    print(f"[corpus] {len(_ingested)} ingested passages loaded from data/corpus/")

#: Fast lookup by id.
BY_ID: dict[str, Passage] = {p.id: p for p in CORPUS}


def get(passage_id: str) -> Passage | None:
    return BY_ID.get(passage_id)
