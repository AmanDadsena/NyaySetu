"""
Second corpus volume: road transport, constitutional detail, and the statutes
people meet in everyday disputes.

Split from `corpus.py` purely so neither file becomes unreadable — both are
loaded together and the retriever treats them as one index.

A note on the money figures below. Motor vehicle penalties are set centrally by
the Motor Vehicles Act but States are empowered to notify their own amounts,
and many have set them lower. Every figure here is therefore described as the
central maximum, with the State caveat attached, because quoting a single
number as *the* fine would be wrong in most of the country.
"""

from __future__ import annotations

from .corpus import INDIA_CODE, Passage

PARIVAHAN = "https://parivahan.gov.in"
ECHALLAN = "https://echallan.parivahan.gov.in"

EXTRA_CORPUS: list[Passage] = [
    # ── Road transport: documents and licensing ─────────────────────────
    Passage(
        id="mv_documents_required",
        title="Documents you must be able to produce while driving",
        act="Motor Vehicles Act, 1988",
        section="Sections 130 and 158; Rule 139, CMVR",
        text=(
            "You must be able to produce a valid driving licence, the certificate of "
            "registration, a valid insurance certificate, and the pollution under control "
            "(PUC) certificate. For a commercial vehicle, add the fitness certificate and "
            "the permit. "
            "Digital copies held in DigiLocker or the mParivahan app are legally valid and "
            "must be accepted — you are not required to carry paper originals. "
            "If you cannot produce a document at the roadside, you may be given fifteen "
            "days to produce it at the designated office rather than being fined on the spot."
        ),
        source_url=PARIVAHAN,
        topics=("traffic", "driving", "documents", "digilocker", "puc", "insurance", "motor vehicle"),
    ),
    Passage(
        id="mv_licence_how_to",
        title="Getting a driving licence",
        act="Motor Vehicles Act, 1988",
        section="Sections 8, 9 and 14",
        text=(
            "You first obtain a learner's licence, valid for six months, after an online "
            "test on road signs and rules. A permanent licence can be applied for after "
            "thirty days and within one hundred and eighty days of the learner's licence, "
            "and requires a driving test. "
            "Minimum age is eighteen for a car or a geared motorcycle, sixteen for a "
            "motorcycle under fifty cc without gears, and twenty for a transport vehicle. "
            "A private licence is valid for twenty years or until age fifty, whichever is "
            "earlier; a transport licence for three years. Apply on the Sarathi portal at "
            "parivahan.gov.in. Renewal is allowed up to one year after expiry without a "
            "fresh test."
        ),
        source_url=PARIVAHAN,
        topics=("driving licence", "learner licence", "sarathi", "traffic", "renewal", "motor vehicle"),
    ),

    # ── Road transport: penalties ───────────────────────────────────────
    Passage(
        id="mv_penalties_core",
        title="Traffic fines after the 2019 amendment",
        act="Motor Vehicles (Amendment) Act, 2019",
        section="Chapter XIII, Sections 177–201",
        text=(
            "These are the central maximum penalties. States may notify lower amounts and "
            "many have, so your State's figure may be less. "
            "General offence, five hundred rupees. Driving without a licence, five thousand. "
            "Driving despite disqualification, ten thousand. Driving without insurance, two "
            "thousand for a first offence and four thousand for a repeat. Over-speeding, one "
            "thousand for light motor vehicles and two thousand for medium or heavy. "
            "Dangerous driving, up to five thousand. Drunk driving, ten thousand and up to "
            "six months' imprisonment for a first offence; fifteen thousand and up to two "
            "years for a second. Using a mobile phone while driving, five thousand. "
            "Not wearing a seat belt, one thousand. Riding without a helmet, one thousand "
            "plus three months' licence disqualification. Overloading a two-wheeler with "
            "more than two people, two thousand plus three months' disqualification. "
            "Racing, five thousand for a first offence. Not giving way to an emergency "
            "vehicle, ten thousand."
        ),
        source_url=ECHALLAN,
        topics=("traffic fine", "challan", "penalty", "drunk driving", "helmet", "seatbelt",
                "overspeeding", "motor vehicle", "traffic"),
    ),
    Passage(
        id="mv_juvenile_offence",
        title="When a minor drives",
        act="Motor Vehicles Act, 1988",
        section="Section 199A",
        text=(
            "Where a minor commits a motor vehicle offence, the guardian or the owner of "
            "the vehicle is deemed guilty unless they prove the offence was committed "
            "without their knowledge or that they exercised due diligence to prevent it. "
            "The penalty is imprisonment up to three years and a fine of twenty-five "
            "thousand rupees. The vehicle's registration is cancelled for twelve months, "
            "and the minor becomes ineligible for a driving licence until the age of "
            "twenty-five. The minor is dealt with under the Juvenile Justice Act."
        ),
        source_url=PARIVAHAN,
        topics=("minor driving", "juvenile", "guardian liability", "traffic", "motor vehicle",
                "underage driving", "son caught driving", "child drove car", "parent liable"),
    ),
    Passage(
        id="echallan_dispute",
        title="Checking, paying and disputing an e-challan",
        act="Motor Vehicles Act, 1988",
        section="Sections 133 and 208",
        text=(
            "Check pending challans by vehicle number, licence number or challan number at "
            "echallan.parivahan.gov.in, or in the mParivahan app. Payment can be made online "
            "there. "
            "You are not obliged to pay a challan you believe is wrong. Every e-challan "
            "carries the option to contest it before the designated traffic court or Lok "
            "Adalat, and the notice states the court and date. Ask for the photographic "
            "evidence — automated challans are camera-generated and number plate misreads do "
            "happen. "
            "Unpaid challans do not simply lapse: they are referred to the virtual court, "
            "and an unresolved challan can block fitness renewal, transfer of ownership and "
            "the issue of a no-objection certificate. Several States hold Lok Adalats where "
            "pending challans are settled at reduced amounts."
        ),
        source_url=ECHALLAN,
        topics=("echallan", "challan", "dispute", "traffic court", "lok adalat", "payment", "traffic"),
    ),
    Passage(
        id="accident_compensation",
        title="Compensation after a road accident",
        act="Motor Vehicles Act, 1988",
        section="Sections 164, 165 and 166",
        text=(
            "Claims go to the Motor Accidents Claims Tribunal for the area where the "
            "accident occurred, or where the claimant or the respondent resides. "
            "Section 164 provides a no-fault structured compensation of five lakh rupees in "
            "case of death and two and a half lakh in case of grievous hurt, payable without "
            "proving negligence. A larger claim on proof of fault can be pursued under "
            "Section 166, which since 2019 has no limitation period. "
            "A hit-and-run victim can claim from the Solatium Fund: two lakh rupees for "
            "death, fifty thousand for grievous hurt. "
            "There is also a golden hour obligation — Section 2(12A) and the cashless "
            "treatment scheme require hospitals to treat accident victims during the first "
            "hour without waiting for payment."
        ),
        source_url=PARIVAHAN,
        topics=("accident", "compensation", "mact", "hit and run", "insurance claim",
                "golden hour", "motor vehicle"),
    ),
    Passage(
        id="vehicle_transfer",
        title="Transferring vehicle ownership",
        act="Motor Vehicles Act, 1988",
        section="Sections 50 and 51",
        text=(
            "The transferor must report the transfer to the registering authority within "
            "fourteen days, and the transferee within thirty days, using Forms 29 and 30. "
            "Moving a vehicle to another State requires a no-objection certificate from the "
            "original registering authority and re-registration within twelve months. "
            "Until the transfer is recorded, the seller remains liable on the record for "
            "challans and, in practice, is dragged into accident claims — so do not treat "
            "handing over the keys and the signed forms as the end of it. Confirm the "
            "transfer has actually been effected on the Vahan portal."
        ),
        source_url=PARIVAHAN,
        topics=("vehicle transfer", "ownership", "noc", "vahan", "rc", "motor vehicle"),
    ),

    # ── Constitution: further detail ────────────────────────────────────
    Passage(
        id="article_14_equality",
        title="Article 14 — equality before the law",
        act="Constitution of India",
        section="Article 14",
        text=(
            "The State shall not deny to any person equality before the law or the equal "
            "protection of the laws within India. It applies to every person, citizen or not. "
            "Equality does not mean identical treatment: the State may classify, provided the "
            "classification rests on an intelligible differentia and that differentia has a "
            "rational nexus with the object sought to be achieved. "
            "Separately, Article 14 forbids arbitrariness in State action — an arbitrary "
            "order is unequal by definition, a principle established in E.P. Royappa and "
            "developed in Maneka Gandhi."
        ),
        source_url="https://legislative.gov.in",
        topics=("article 14", "equality", "arbitrary", "constitution", "fundamental rights"),
    ),
    Passage(
        id="article_19_freedoms",
        title="Article 19 — the six freedoms and their limits",
        act="Constitution of India",
        section="Article 19",
        text=(
            "Citizens have the right to freedom of speech and expression; to assemble "
            "peaceably and without arms; to form associations or unions; to move freely "
            "throughout India; to reside and settle in any part of India; and to practise any "
            "profession or carry on any occupation, trade or business. "
            "Each may be restricted only by a law imposing reasonable restrictions on the "
            "grounds listed in the article itself — for speech, these are the sovereignty and "
            "integrity of India, the security of the State, friendly relations with foreign "
            "States, public order, decency or morality, contempt of court, defamation, and "
            "incitement to an offence. A restriction outside those grounds is unconstitutional "
            "however desirable it may seem. "
            "In Shreya Singhal (2015) the Supreme Court struck down Section 66A of the IT Act "
            "for vagueness and overbreadth."
        ),
        source_url="https://legislative.gov.in",
        topics=("article 19", "free speech", "assembly", "protest", "constitution",
                "fundamental rights", "shreya singhal"),
    ),
    Passage(
        id="article_23_24",
        title="Right against exploitation — forced and child labour",
        act="Constitution of India",
        section="Articles 23 and 24",
        text=(
            "Article 23 prohibits traffic in human beings, begar and other similar forms of "
            "forced labour, and makes contravention an offence. The Supreme Court held in "
            "PUDR v. Union of India (1982) that paying less than the minimum wage amounts to "
            "forced labour under this article. "
            "Article 24 prohibits the employment of any child below fourteen in a factory, "
            "mine or other hazardous employment. The Child and Adolescent Labour (Prohibition "
            "and Regulation) Act, 1986 gives effect to it, and the Bonded Labour System "
            "(Abolition) Act, 1976 abolished bonded labour and cancelled outstanding bonded "
            "debts."
        ),
        source_url="https://legislative.gov.in",
        topics=("child labour", "forced labour", "bonded labour", "trafficking",
                "article 23", "constitution", "minimum wage"),
    ),
    Passage(
        id="article_25_religion",
        title="Freedom of religion",
        act="Constitution of India",
        section="Articles 25 to 28",
        text=(
            "All persons are equally entitled to freedom of conscience and the right freely "
            "to profess, practise and propagate religion, subject to public order, morality, "
            "health and the other Fundamental Rights. "
            "The State may regulate secular activity associated with religious practice and "
            "may legislate for social welfare and reform, including throwing open Hindu "
            "religious institutions to all classes. "
            "Religious denominations may manage their own affairs in matters of religion "
            "under Article 26. Courts apply the essential religious practices test to decide "
            "what the guarantee actually protects."
        ),
        source_url="https://legislative.gov.in",
        topics=("religion", "article 25", "freedom of conscience", "constitution",
                "fundamental rights"),
    ),
    Passage(
        id="article_21a_education",
        title="Right to education",
        act="Constitution of India and Right of Children to Free and Compulsory Education Act, 2009",
        section="Article 21A; RTE Act Sections 3, 12 and 16",
        text=(
            "The State shall provide free and compulsory education to all children aged six "
            "to fourteen. Under the RTE Act no child may be denied admission for want of "
            "documents, may be held back or expelled before completing elementary education, "
            "or be subjected to physical punishment or mental harassment. "
            "Private unaided schools must reserve at least twenty-five per cent of entry-level "
            "seats for children from disadvantaged groups and weaker sections, with the State "
            "reimbursing the fee. Capitation fees and screening procedures for admission are "
            "prohibited."
        ),
        source_url=INDIA_CODE,
        topics=("education", "rte", "school admission", "article 21a", "children",
                "constitution"),
    ),
    Passage(
        id="directive_principles",
        title="Directive Principles of State Policy",
        act="Constitution of India",
        section="Part IV, Articles 36–51",
        text=(
            "The Directive Principles set goals for governance — adequate means of livelihood, "
            "equal pay for equal work, protection of workers and children, free legal aid "
            "(Article 39A), village panchayats, the right to work and education, a living "
            "wage, participation of workers in management, a uniform civil code (Article 44), "
            "early childhood care, protection of the environment, and separation of the "
            "judiciary from the executive. "
            "They are expressly not enforceable by any court under Article 37, but are "
            "fundamental in the governance of the country and courts use them to interpret "
            "Fundamental Rights. Article 39A is the constitutional basis for the legal "
            "services authorities."
        ),
        source_url="https://legislative.gov.in",
        topics=("directive principles", "dpsp", "article 39a", "legal aid", "constitution",
                "uniform civil code"),
    ),
    Passage(
        id="fundamental_duties",
        title="Fundamental Duties",
        act="Constitution of India",
        section="Part IVA, Article 51A",
        text=(
            "Every citizen has duties: to abide by the Constitution and respect its ideals, "
            "the National Flag and the National Anthem; to cherish the ideals of the freedom "
            "struggle; to uphold the sovereignty, unity and integrity of India; to defend the "
            "country; to promote harmony and renounce practices derogatory to the dignity of "
            "women; to value the composite culture; to protect the natural environment; to "
            "develop a scientific temper; to safeguard public property and abjure violence; "
            "to strive towards excellence; and to provide education to one's child between "
            "six and fourteen. "
            "These were added by the Forty-second Amendment in 1976 and are not directly "
            "enforceable."
        ),
        source_url="https://legislative.gov.in",
        topics=("fundamental duties", "article 51a", "constitution", "citizen"),
    ),
    Passage(
        id="emergency_provisions",
        title="Emergency provisions",
        act="Constitution of India",
        section="Articles 352, 356 and 360",
        text=(
            "A National Emergency under Article 352 may be proclaimed on grounds of war, "
            "external aggression or armed rebellion — 'internal disturbance' was replaced by "
            "'armed rebellion' by the Forty-fourth Amendment after the 1975 Emergency. It "
            "requires the written advice of the Cabinet and approval by both Houses by a "
            "special majority within a month. "
            "President's Rule under Article 356 applies where the government of a State cannot "
            "be carried on in accordance with the Constitution; S.R. Bommai (1994) made the "
            "proclamation subject to judicial review. "
            "A Financial Emergency under Article 360 has never been declared. "
            "Article 20 and Article 21 cannot be suspended even during an Emergency."
        ),
        source_url="https://legislative.gov.in",
        topics=("emergency", "article 352", "president's rule", "article 356", "constitution",
                "bommai"),
    ),

    # ── Everyday statutes ───────────────────────────────────────────────
    Passage(
        id="contract_essentials",
        title="What makes an agreement legally enforceable",
        act="Indian Contract Act, 1872",
        section="Sections 10, 11, 23 and 25",
        text=(
            "An agreement is a contract if it is made by the free consent of parties competent "
            "to contract, for a lawful consideration and a lawful object, and is not expressly "
            "declared void. "
            "A person is competent if they are of the age of majority, of sound mind, and not "
            "disqualified by law; an agreement by a minor is void from the beginning. "
            "Consent is not free if obtained by coercion, undue influence, fraud, "
            "misrepresentation or mistake. "
            "An agreement without consideration is generally void, with narrow exceptions "
            "including a written and registered promise made out of natural love and affection "
            "between parties in a near relation."
        ),
        source_url=INDIA_CODE,
        topics=("contract", "agreement", "consideration", "minor", "consent", "void"),
    ),
    Passage(
        id="contract_restraint",
        title="Non-compete clauses after employment ends",
        act="Indian Contract Act, 1872",
        section="Section 27",
        text=(
            "Every agreement by which anyone is restrained from exercising a lawful "
            "profession, trade or business is void to that extent, with a narrow exception "
            "for the sale of goodwill. "
            "Indian courts have consistently held that a restraint operating *after* "
            "employment ends is void under Section 27, however reasonable it looks — unlike "
            "England, there is no reasonableness test to save it. Restraints during "
            "employment, such as exclusivity while employed, are generally enforceable. "
            "Confidentiality obligations and protection of trade secrets survive separately "
            "and are not affected by this."
        ),
        source_url=INDIA_CODE,
        topics=("non-compete", "restraint of trade", "employment", "section 27", "contract",
                "notice period"),
    ),
    Passage(
        id="limitation_periods",
        title="Time limits for filing a case",
        act="Limitation Act, 1963",
        section="Schedule; Sections 3 and 5",
        text=(
            "A suit filed after the prescribed period is dismissed even if nobody raises the "
            "point. Common periods, running from when the right to sue accrues: three years "
            "for a suit on a contract or for recovery of money; three years for compensation "
            "for most torts, but one year for defamation; twelve years for possession of "
            "immovable property; thirty years for a mortgage. "
            "An appeal to a High Court from a decree is ninety days; to a District Court, "
            "thirty days. "
            "An acknowledgement of liability in writing before the period expires starts the "
            "clock again. Delay in an appeal may be condoned under Section 5 on sufficient "
            "cause, but this does not apply to the original suit."
        ),
        source_url=INDIA_CODE,
        topics=("limitation", "time limit", "deadline", "filing", "appeal", "suit",
                "how long do i have to file", "how much time to file a case", "too late to sue"),
        also_known_as=("time barred", "limitation period", "how long to file a civil suit"),
    ),
    Passage(
        id="defamation",
        title="Defamation, civil and criminal",
        act="Bharatiya Nyaya Sanhita, 2023 and common law",
        section="BNS Sections 356",
        text=(
            "Criminal defamation is punishable with simple imprisonment up to two years, or a "
            "fine, or both, or community service. The offence requires publication to a third "
            "party of an imputation intended to harm, or known to be likely to harm, a "
            "person's reputation. "
            "There are statutory exceptions: truth published for the public good, fair comment "
            "on the conduct of a public servant or on a public question, a substantially true "
            "report of court proceedings, and a good-faith accusation to a lawful authority. "
            "A civil suit for damages is separate and needs only the balance of probabilities. "
            "The Supreme Court upheld the constitutionality of criminal defamation in "
            "Subramanian Swamy (2016)."
        ),
        source_url=INDIA_CODE,
        topics=("defamation", "reputation", "libel", "slander", "free speech",
                "spreading lies", "false statements", "rumours", "character assassination",
                "insulted publicly", "damaged my reputation"),
        also_known_as=("Section 499 IPC", "Section 500 IPC"),
    ),
    Passage(
        id="data_protection",
        title="Your rights over your personal data",
        act="Digital Personal Data Protection Act, 2023",
        section="Sections 5–14",
        text=(
            "Personal data may be processed only for a lawful purpose with your consent, or "
            "for certain legitimate uses. A notice must tell you what data is collected and "
            "why, in English or any language in the Eighth Schedule. "
            "You have the right to access a summary of your data, to correction and erasure, "
            "to nominate someone to exercise your rights if you die or become incapacitated, "
            "and to a grievance redressal mechanism. Consent must be as easy to withdraw as "
            "to give. "
            "Children's data requires verifiable parental consent, and behavioural advertising "
            "directed at children is prohibited. "
            "Complaints go to the Data Protection Board, and penalties for a data breach run "
            "to two hundred and fifty crore rupees."
        ),
        source_url=INDIA_CODE,
        topics=("data protection", "privacy", "dpdp", "consent", "personal data", "breach"),
    ),
    Passage(
        id="police_complaint_against",
        title="Complaining about the police",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023 and Prakash Singh directions",
        section="Prakash Singh v. Union of India (2006) 8 SCC 1",
        text=(
            "Complaints against police officers can be made to the Superintendent of Police "
            "or the Commissioner, to the Police Complaints Authority that every State was "
            "directed to constitute in Prakash Singh, to the State or National Human Rights "
            "Commission, or by way of a private complaint to the Magistrate. "
            "Custodial death or rape must be reported to the National Human Rights Commission "
            "within twenty-four hours, and a magisterial inquiry is mandatory. "
            "For an offence alleged to have been committed by a public servant while acting "
            "in the discharge of official duty, a preliminary inquiry and government sanction "
            "may be required before prosecution, which is a real practical hurdle."
        ),
        source_url="https://nhrc.nic.in",
        topics=("police complaint", "custodial death", "nhrc", "misconduct", "prakash singh",
                "human rights"),
    ),
    Passage(
        id="missing_person",
        title="If someone goes missing",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 173",
        text=(
            "Police must register a report immediately. There is no rule requiring you to wait "
            "twenty-four hours before reporting a missing person — that is a myth, and where "
            "the missing person is a child the Supreme Court directed in Bachpan Bachao Andolan "
            "that an FIR be registered at once on the presumption of kidnapping or trafficking. "
            "Details are uploaded to the national Zonal Integrated Police Network and the "
            "TrackChild portal. "
            "If the police refuse, the escalation route is the Superintendent of Police, then "
            "the Magistrate, and the childline number 1098 or the women's helpline 181 can "
            "assist."
        ),
        source_url="https://trackthemissingchild.gov.in",
        topics=("missing person", "kidnapping", "children", "fir", "police", "1098"),
    ),
    Passage(
        id="mental_healthcare",
        title="Rights of a person with mental illness",
        act="Mental Healthcare Act, 2017",
        section="Sections 18, 19, 21 and 115",
        text=(
            "Every person has a right to access mental healthcare run or funded by the "
            "government, and to community living — a person cannot be kept in a mental health "
            "establishment merely because their family will not take them. "
            "Insurers must provide for mental illness on the same basis as physical illness. "
            "A person may make an advance directive stating how they wish to be treated, and "
            "appoint a nominated representative. "
            "Section 115 presumes that a person who attempts suicide is under severe stress "
            "and shall not be prosecuted, effectively decriminalising the attempt. "
            "Free legal services are available to exercise any right under the Act."
        ),
        source_url=INDIA_CODE,
        topics=("mental health", "disability", "insurance", "suicide", "advance directive",
                "healthcare"),
    ),
    Passage(
        id="disability_rights",
        title="Rights of persons with disabilities",
        act="Rights of Persons with Disabilities Act, 2016",
        section="Sections 3, 32, 34 and 40",
        text=(
            "Twenty-one disabilities are recognised. Discrimination on the ground of "
            "disability is prohibited, and the government must ensure reasonable accommodation. "
            "Four per cent of posts in government establishments are reserved for persons with "
            "benchmark disabilities, and five per cent of seats in government and "
            "government-aided higher education institutions. "
            "Public buildings, transport and websites must meet accessibility standards. "
            "A person with a benchmark disability is entitled to a certificate through the "
            "online UDID system, which unlocks concessions and scheme benefits. "
            "Complaints go to the State or Chief Commissioner for Persons with Disabilities."
        ),
        source_url=INDIA_CODE,
        topics=("disability", "accessibility", "reservation", "udid", "discrimination",
                "rights"),
    ),
    Passage(
        id="e_commerce_rights",
        title="Buying online — your rights",
        act="Consumer Protection (E-Commerce) Rules, 2020",
        section="Rules 4, 5 and 6",
        text=(
            "Every e-commerce entity must display the seller's legal name and address, the "
            "total price with a break-up of all charges, the country of origin, the expected "
            "delivery time, and the return, refund, exchange and warranty policy. "
            "Cancellation charges cannot be imposed unless the platform bears similar charges "
            "itself. Refunds must be processed within a reasonable period. "
            "Manipulating prices to make an unreasonable profit, and discriminating between "
            "consumers of the same class, are prohibited. Every platform must appoint a "
            "grievance officer who acknowledges a complaint within forty-eight hours and "
            "resolves it within one month."
        ),
        source_url="https://consumerhelpline.gov.in",
        topics=("e-commerce", "online shopping", "refund", "return", "consumer",
                "grievance officer"),
    ),
    Passage(
        id="banking_fraud_liability",
        title="If money is taken from your bank account",
        act="RBI Circular on Customer Protection, 2017",
        section="Limiting Liability of Customers in Unauthorised Electronic Transactions",
        text=(
            "Your liability depends almost entirely on how fast you report. If the fraud is "
            "due to the bank's negligence, or a third-party breach where neither you nor the "
            "bank is at fault and you report within three working days, your liability is "
            "zero. Reporting on the fourth to seventh working day limits liability to between "
            "five thousand and twenty-five thousand rupees depending on account type. Beyond "
            "seven days, the bank's board-approved policy applies. "
            "Where the loss is due to your own negligence, such as sharing an OTP or PIN, you "
            "bear the loss until you report it. "
            "Banks must credit the disputed amount within ten working days of notification. "
            "Report to the bank in writing, and on the cyber helpline 1930. Unresolved "
            "complaints go to the RBI Ombudsman at cms.rbi.org.in after thirty days."
        ),
        source_url="https://cms.rbi.org.in",
        topics=("bank fraud", "unauthorised transaction", "otp", "rbi", "ombudsman",
                "cyber fraud", "refund", "1930"),
    ),
    Passage(
        id="insurance_claim_rejected",
        title="If an insurance claim is rejected",
        act="Insurance Regulatory and Development Authority (Protection of Policyholders' Interests) Regulations, 2017",
        section="Regulations 8, 14 and 17",
        text=(
            "An insurer must settle or reject a claim within thirty days of receiving the last "
            "necessary document, and must give reasons in writing for a rejection. Where an "
            "investigation is required it must be completed within thirty days and the claim "
            "settled within forty-five days. Delay attracts interest at two per cent above the "
            "bank rate. "
            "A life policy cannot be repudiated on the ground of misstatement after three "
            "years from commencement or revival, under Section 45 of the Insurance Act — this "
            "is an absolute bar. "
            "Escalate to the insurer's grievance cell, then the IRDAI Bima Bharosa portal, "
            "then the Insurance Ombudsman, which is free and handles claims up to fifty lakh "
            "rupees. A consumer commission is also available."
        ),
        source_url="https://bimabharosa.irdai.gov.in",
        topics=("insurance", "claim rejected", "irdai", "ombudsman", "policy", "section 45"),
    ),
    Passage(
        id="wage_theft",
        title="If your employer does not pay you",
        act="Code on Wages, 2019",
        section="Sections 17, 43 and 45",
        text=(
            "Wages must be paid before the seventh day after the last day of the wage period "
            "for establishments with fewer than a thousand workers, and before the tenth "
            "otherwise. On termination, resignation or retrenchment, wages are due within two "
            "working days. "
            "Unauthorised deductions are limited and cannot in total exceed fifty per cent of "
            "wages. "
            "File a claim with the authority appointed under the Code; the limitation period "
            "is three years, considerably longer than the one year under the old Payment of "
            "Wages Act. The authority can order payment plus compensation of up to ten times "
            "the amount withheld. There is no court fee, and an inspector-cum-facilitator can "
            "file on your behalf."
        ),
        source_url="https://labour.gov.in",
        topics=("unpaid salary", "wages", "employer", "deduction", "employment", "claim"),
    ),
    Passage(
        id="rti_exemptions",
        title="What information can be refused under RTI",
        act="Right to Information Act, 2005",
        section="Sections 8 and 24",
        text=(
            "Exemptions include information affecting sovereignty and integrity, security, "
            "strategic or economic interests; information forbidden by a court; breach of "
            "parliamentary privilege; commercial confidence, trade secrets or intellectual "
            "property where disclosure harms a third party; information held in a fiduciary "
            "relationship; information received in confidence from a foreign government; "
            "information endangering life or physical safety or identifying a confidential "
            "source; information impeding investigation or prosecution; cabinet papers before "
            "a decision is taken; and personal information with no relationship to public "
            "activity. "
            "Even exempt information must be disclosed if the public interest in disclosure "
            "outweighs the protected interest, under Section 8(2). Information which cannot "
            "be denied to Parliament or a State Legislature cannot be denied to you."
        ),
        source_url="https://cic.gov.in",
        topics=("rti", "exemption", "section 8", "refusal", "public interest", "transparency"),
    ),
    Passage(
        id="passport_police_verification",
        title="Passport applications and adverse police verification",
        act="Passports Act, 1967",
        section="Sections 5, 6 and 11",
        text=(
            "A passport may be refused on specified grounds, including that criminal "
            "proceedings are pending before a court in India. Where proceedings are pending, "
            "a passport can still be issued if the court grants a no-objection order. "
            "A refusal or impounding must be accompanied by a written statement of reasons, "
            "and an appeal lies to the appellate authority within thirty days. "
            "This is the area Maneka Gandhi decided: the right to travel abroad is part of "
            "personal liberty under Article 21, so a passport cannot be impounded without a "
            "fair procedure and an opportunity to be heard."
        ),
        source_url="https://passportindia.gov.in",
        topics=("passport", "police verification", "travel", "article 21", "maneka gandhi"),
    ),
    Passage(
        id="noise_pollution",
        title="Noise limits and loudspeakers",
        act="Noise Pollution (Regulation and Control) Rules, 2000",
        section="Rules 3–5",
        text=(
            "Ambient limits during the day and night: industrial areas seventy-five and "
            "seventy decibels; commercial sixty-five and fifty-five; residential fifty-five "
            "and forty-five; silence zones fifty and forty. Night runs from ten at night to "
            "six in the morning. "
            "Loudspeakers may not be used at night at all except in closed premises, with a "
            "narrow State exemption of up to fifteen days a year for cultural or religious "
            "occasions, and even then only until midnight. "
            "A silence zone extends one hundred metres around hospitals, educational "
            "institutions and courts. "
            "Complain to the local police, the pollution control board, or on the national "
            "noise pollution helpline; a violation is an offence under the Environment "
            "(Protection) Act, 1986."
        ),
        source_url=INDIA_CODE,
        topics=("noise", "loudspeaker", "pollution", "nuisance", "neighbour", "complaint"),
    ),
    Passage(
        id="succession_certificate",
        title="Claiming a deceased person's bank balance and investments",
        act="Indian Succession Act, 1925",
        section="Sections 370–390",
        text=(
            "A succession certificate is granted by a civil court to the legal heirs of a "
            "person who died without a will, and authorises collection of debts and securities "
            "— bank balances, fixed deposits, shares. Apply to the District Judge where the "
            "deceased ordinarily resided, with the death certificate and proof of "
            "relationship. The court issues a newspaper notice, usually allowing forty-five "
            "days for objections. "
            "Where there is a will, the executor seeks probate instead; in Bengal, Bihar, "
            "Odisha, Assam and the mofussil areas of Mumbai and Chennai, probate is mandatory. "
            "A legal heir certificate from the tehsildar is a lighter document and is often "
            "sufficient for pension and provident fund claims. "
            "Nomination is not inheritance: a nominee holds for the legal heirs."
        ),
        source_url=INDIA_CODE,
        topics=("succession certificate", "probate", "will", "inheritance", "bank account",
                "legal heir", "nominee"),
    ),
]
