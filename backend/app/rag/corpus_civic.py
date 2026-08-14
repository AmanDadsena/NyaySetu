"""
Third corpus volume: civil procedure, housing, money, work and civic life.

The first two volumes cover the moments when the State comes to you — arrest,
FIR, challan, prosecution. This one covers the far commoner case where you have
to go to the State, or to a company, and make something happen: a builder who
will not hand over a flat, a bank that will not reverse a fraudulent debit, an
employer withholding provident fund, a municipal office that will not issue a
certificate.

Two conventions carried over from the earlier volumes. Money thresholds are
given with the caveat that States notify their own figures where the statute
lets them, because quoting one number as *the* limit is wrong in most of the
country. And where a body was renamed or a forum restructured, the old name
stays in `also_known_as` so a search using it still lands.
"""

from __future__ import annotations

from .corpus import INDIA_CODE, Passage

CONSUMER_HELPLINE = "https://consumerhelpline.gov.in"
RBI = "https://www.rbi.org.in"

CIVIC_CORPUS: list[Passage] = [
    # ── Civil procedure: getting into court ─────────────────────────────
    Passage(
        id="legal_notice_before_suit",
        title="Sending a legal notice before you sue",
        act="Code of Civil Procedure, 1908",
        section="Section 80 for government defendants; otherwise contractual or statutory",
        text=(
            "A legal notice states your claim, gives the other side a deadline to meet it, and "
            "warns that you will sue if they do not. For most private disputes it is not legally "
            "compulsory, but it is worth sending: it often settles the matter without a case, and "
            "it fixes your version of events in writing before anyone has a reason to change their "
            "story. Send it by registered post with acknowledgement due, and keep the receipt and "
            "the tracking record — that proof of service is what you will rely on later. "
            "Where the defendant is the government or a public officer acting officially, a notice "
            "under Section 80 is mandatory and the suit cannot be filed until two months have "
            "passed. A cheque bounce notice under Section 138 has its own strict deadline: 30 days "
            "from the bank's memo."
        ),
        source_url=INDIA_CODE,
        topics=("legal notice", "before suing", "demand", "section 80", "registered post"),
        also_known_as=("notice period", "demand letter", "advocate notice"),
    ),
    Passage(
        id="civil_suit_how_to_file",
        title="How a civil suit is filed",
        act="Code of Civil Procedure, 1908",
        section="Order VI and Order VII",
        text=(
            "A civil suit begins with a plaint: a numbered statement of who the parties are, what "
            "happened, why this particular court can hear it, what you want, and what the claim is "
            "worth. It is filed with the documents you rely on, a list of witnesses, and the court "
            "fee for the value of the claim. Which court hears it depends on both the value of the "
            "suit and where the cause of action arose or the defendant resides. "
            "The court issues summons; the defendant files a written statement, normally within 30 "
            "days and at most 90. Failing to file in time can cost the right to defend. "
            "A suit must be filed within the limitation period — usually three years for contract "
            "and recovery, twelve years for immovable property. A suit filed late is dismissed "
            "however strong the merits."
        ),
        source_url=INDIA_CODE,
        topics=("civil suit", "plaint", "written statement", "jurisdiction", "court fee"),
        also_known_as=("filing a case", "order 7 rule 11", "civil case"),
    ),
    Passage(
        id="court_fees_basics",
        title="What it costs to file, and getting it waived",
        act="Court Fees Act, 1870 and State amendments",
        section="Sections 6–7; Order XXXIII CPC",
        text=(
            "Court fee is usually a percentage of what you are claiming, set by each State, so the "
            "same suit costs different amounts in different States. Some proceedings carry a fixed "
            "fee instead: writ petitions, most consumer complaints below the lowest slab, and "
            "matrimonial petitions. "
            "If you genuinely cannot afford the fee you can sue as an indigent person under Order "
            "XXXIII CPC — you file the same plaint with an application showing you lack the means, "
            "and if the court accepts it the fee is not payable up front. Free legal aid under the "
            "Legal Services Authorities Act covers court fees as well as a lawyer. "
            "When a case settles at a Lok Adalat the court fee already paid is refunded in full."
        ),
        source_url=INDIA_CODE,
        topics=("court fee", "cost of filing", "indigent", "fee waiver", "refund"),
        also_known_as=("pauper suit", "in forma pauperis"),
    ),
    Passage(
        id="arbitration_basics",
        title="When your contract says disputes go to arbitration",
        act="Arbitration and Conciliation Act, 1996",
        section="Sections 7, 8, 11 and 34",
        text=(
            "If the contract contains an arbitration clause, a court will normally refuse to hear "
            "the dispute and send you to arbitration instead. One arbitrator decides — or three, if "
            "the clause says so — and the parties share the cost, which is the main drawback for a "
            "small claim. If the parties cannot agree on who arbitrates, the High Court appoints "
            "under Section 11. "
            "The award is binding. It can be challenged in court under Section 34 only on narrow "
            "grounds — incapacity, an invalid agreement, no proper notice, the award going beyond "
            "the reference, or conflict with public policy — and not because the arbitrator got the "
            "facts or the law wrong. The challenge must be filed within three months. "
            "A consumer can still go to a consumer commission despite an arbitration clause; that "
            "right is not taken away by contract."
        ),
        source_url=INDIA_CODE,
        topics=("arbitration", "arbitration clause", "award", "section 34", "contract dispute"),
        also_known_as=("adr", "alternative dispute resolution"),
    ),
    Passage(
        id="mediation_pre_litigation",
        title="Mediation before going to court",
        act="Mediation Act, 2023",
        section="Sections 5 and 8; Section 12A, Commercial Courts Act, 2015",
        text=(
            "Mediation is a negotiation run by a neutral third person who has no power to impose "
            "anything. Nothing said in it can be used later in court, and either side can walk away. "
            "If it succeeds, the settlement is signed and enforceable in the same way as a court "
            "decree. "
            "For commercial disputes that do not seek urgent interim relief, pre-litigation "
            "mediation under Section 12A of the Commercial Courts Act is mandatory before a suit "
            "can be filed. Court-annexed mediation centres operate in most district courts and are "
            "free or nearly free. Family courts routinely refer matrimonial disputes to mediation "
            "before hearing them."
        ),
        source_url=INDIA_CODE,
        topics=("mediation", "settlement", "pre-litigation", "family court", "commercial"),
        also_known_as=("conciliation", "section 12a"),
    ),
    Passage(
        id="injunction_stay",
        title="Stopping something from happening while the case runs",
        act="Code of Civil Procedure, 1908 and Specific Relief Act, 1963",
        section="Order XXXIX Rules 1–2 CPC; Sections 36–42, Specific Relief Act",
        text=(
            "An injunction orders someone to stop doing something — demolishing a wall, selling a "
            "disputed plot, dismissing you pending inquiry. To get a temporary injunction while the "
            "suit is pending you must show three things together: a serious question to be tried, "
            "that you will suffer harm money cannot repair, and that the balance of convenience "
            "favours you. Missing any one of them normally defeats the application. "
            "In an emergency the court can grant an ex parte injunction without hearing the other "
            "side, but it must then be served immediately and the court must dispose of the "
            "application within 30 days. Disobeying an injunction is punishable under Order XXXIX "
            "Rule 2A by attachment of property or civil imprisonment."
        ),
        source_url=INDIA_CODE,
        topics=("injunction", "stay order", "interim relief", "status quo", "restraining"),
        also_known_as=("stay", "order 39", "temporary injunction"),
    ),

    # ── Housing, land and the builder ───────────────────────────────────
    Passage(
        id="rera_homebuyer",
        title="If a builder delays or misdescribes your flat",
        act="Real Estate (Regulation and Development) Act, 2016",
        section="Sections 12, 14, 18 and 31",
        text=(
            "Every project above 500 square metres or eight apartments must be registered with the "
            "State RERA before it is advertised or sold. Check the registration number on the State "
            "RERA website before paying anything. "
            "If possession is delayed beyond the date in the agreement you may either withdraw and "
            "get the entire amount back with interest, or stay in the project and claim interest "
            "for every month of delay — the choice is yours, not the builder's. If the flat does "
            "not match what was promised in the sanctioned plan or the prospectus, Section 14 "
            "requires it to be rectified; structural defects must be repaired free for five years "
            "from possession. "
            "A builder cannot take more than ten per cent of the cost before a written agreement "
            "for sale is signed. Complaints go to the State RERA authority, with appeal to the RERA "
            "Appellate Tribunal."
        ),
        source_url=INDIA_CODE,
        topics=("rera", "builder", "flat", "possession delay", "real estate", "refund"),
        also_known_as=("real estate regulatory authority", "housing project", "apartment"),
    ),
    Passage(
        id="property_mutation",
        title="Getting the revenue records changed after you buy",
        act="State land revenue codes; Registration Act, 1908",
        section="Varies by State",
        text=(
            "Registration and mutation are different things and buyers routinely confuse them. "
            "Registration records the transfer of title at the sub-registrar's office. Mutation "
            "(dakhil kharij, khata transfer) updates the revenue or municipal record so that tax "
            "demands and utility bills come to you. "
            "Mutation does not by itself create ownership and a mutation entry is not proof of "
            "title — courts have said so repeatedly. But without it you will struggle to pay "
            "property tax, get a water or electricity connection transferred, or sell on. "
            "Apply at the tehsil, municipal or panchayat office with the registered sale deed, the "
            "previous owner's details, tax receipts and an affidavit. Most States now accept this "
            "online and prescribe a time limit for disposal."
        ),
        source_url=INDIA_CODE,
        topics=("mutation", "khata", "revenue record", "property tax", "dakhil kharij"),
        also_known_as=("namantaran", "khata transfer", "record of rights"),
    ),
    Passage(
        id="encumbrance_certificate",
        title="Checking a property is free of loans and disputes",
        act="Registration Act, 1908",
        section="Sections 57 and 74",
        text=(
            "An encumbrance certificate lists the registered transactions affecting a property over "
            "a period you choose — sales, mortgages, gifts, leases, court attachments. It is the "
            "single most useful document to obtain before buying, because it reveals an existing "
            "home loan or an earlier sale of the same plot. "
            "Apply at the sub-registrar's office for the area, or online in most States, giving the "
            "survey number and the period; thirteen to thirty years is normal for a purchase. "
            "It has one important limit: it only shows what was *registered*. An unregistered "
            "agreement, an oral family arrangement or a pending suit may not appear, so it is worth "
            "also obtaining the parent documents and a title search."
        ),
        source_url=INDIA_CODE,
        topics=("encumbrance certificate", "ec", "property search", "mortgage", "buying land"),
        also_known_as=("ec", "title search", "nil encumbrance"),
    ),
    Passage(
        id="partition_property",
        title="Dividing family property between co-owners",
        act="Code of Civil Procedure, 1908 and Hindu Succession Act, 1956",
        section="Order XX Rule 18 CPC; Section 6, Hindu Succession Act",
        text=(
            "Any co-owner may demand partition; nobody can be forced to stay in joint ownership. "
            "The cleanest route is a registered partition deed signed by everyone, which must be "
            "stamped and registered to be effective for immovable property. A family settlement "
            "recording an existing arrangement can sometimes be oral, but a document that itself "
            "creates rights must be registered. "
            "If the co-owners will not agree, file a partition suit. The court first passes a "
            "preliminary decree declaring each person's share, then a final decree dividing the "
            "property by metes and bounds — or ordering a sale and division of the proceeds where "
            "physical division is impractical. "
            "Since the 2005 amendment a daughter is a coparcener by birth on the same footing as a "
            "son, and the Supreme Court has confirmed this applies whether or not the father was "
            "alive in 2005."
        ),
        source_url=INDIA_CODE,
        topics=("partition", "co-owner", "family property", "share", "ancestral",
                "divide property between brothers", "brother will not divide",
                "father's land", "splitting inherited land"),
        also_known_as=("partition suit", "batwara", "division of property",
                       "divide our father's land", "brothers dividing property"),
    ),
    Passage(
        id="gift_deed",
        title="Giving property away, and whether it can be taken back",
        act="Transfer of Property Act, 1882 and Registration Act, 1908",
        section="Sections 122–126, Transfer of Property Act",
        text=(
            "A gift of immovable property must be made by a registered instrument signed by the "
            "donor and attested by two witnesses, and it must be accepted by the donee while the "
            "donor is alive. An unregistered gift of immovable property transfers nothing. Stamp "
            "duty is usually lower for a gift to a close relative, and several States charge a "
            "nominal amount. "
            "A completed gift cannot ordinarily be revoked merely because the donor changed their "
            "mind. It can be revoked only on a condition agreed at the time of the gift, or if it "
            "was obtained by fraud, coercion or undue influence. "
            "There is one important exception for elderly donors: under the Maintenance and Welfare "
            "of Parents and Senior Citizens Act, a transfer made on the condition that the "
            "transferee will look after the senior citizen can be declared void by the Maintenance "
            "Tribunal if they then fail to do so."
        ),
        source_url=INDIA_CODE,
        topics=("gift deed", "transfer", "revocation", "stamp duty", "senior citizen"),
        also_known_as=("hiba", "settlement deed", "danpatra"),
    ),
    Passage(
        id="lease_vs_licence",
        title="Lease or leave-and-licence, and why the difference matters",
        act="Transfer of Property Act, 1882 and Indian Easements Act, 1882",
        section="Sections 105–107, Transfer of Property Act; Section 52, Easements Act",
        text=(
            "A lease transfers an interest in the property and gives the tenant exclusive "
            "possession. A licence only permits use and creates no interest in the land. What the "
            "document is called does not decide which it is — courts look at whether exclusive "
            "possession was actually given. "
            "The distinction matters because a lease attracts rent-control protection in many "
            "States and a licence generally does not, and because a lessee cannot simply be locked "
            "out whereas a licence can be revoked on its terms. "
            "A lease of immovable property from year to year, or for more than one year, must be "
            "made by a registered instrument. Most residential arrangements are therefore written "
            "for eleven months, which avoids compulsory registration. Maharashtra and some other "
            "States require even leave-and-licence agreements to be registered."
        ),
        source_url=INDIA_CODE,
        topics=("lease", "licence", "rent agreement", "eleven months", "possession"),
        also_known_as=("leave and licence", "rental agreement", "11 month agreement"),
    ),
    Passage(
        id="land_acquisition_compensation",
        title="When the government takes your land",
        act="Right to Fair Compensation and Transparency in Land Acquisition, "
            "Rehabilitation and Resettlement Act, 2013",
        section="Sections 4, 26–30 and 24",
        text=(
            "Acquisition must be preceded by a Social Impact Assessment, and for private projects "
            "by the consent of a proportion of affected families — seventy per cent for "
            "public-private partnerships and eighty per cent for private companies. "
            "Compensation is the market value multiplied by a factor of one in urban areas and up "
            "to two in rural areas, plus the value of assets attached to the land, plus a hundred "
            "per cent solatium on that total. Rehabilitation and resettlement entitlements under "
            "the Second Schedule are additional and apply to those who lose livelihood as well as "
            "landowners. "
            "Objections are filed under Section 15 within sixty days of the preliminary "
            "notification. Compensation is decided by the Collector and can be referred to the "
            "Land Acquisition, Rehabilitation and Resettlement Authority."
        ),
        source_url=INDIA_CODE,
        topics=("land acquisition", "compensation", "solatium", "rehabilitation", "government"),
        also_known_as=("larr act", "bhoomi adhigrahan", "acquisition notice"),
    ),
    Passage(
        id="housing_society_dispute",
        title="Disputes with a housing society or RWA",
        act="State Cooperative Societies Acts; Model Bye-laws",
        section="Varies by State; commonly the Registrar and the Cooperative Court",
        text=(
            "A society cannot cut off your water or electricity, deny you the lift, or stop your "
            "domestic help entering because maintenance is unpaid. Courts and State registrars "
            "have consistently held such measures illegal; the society's remedy is to recover the "
            "dues, with interest as the bye-laws allow, not to make life unliveable. "
            "Maintenance must be charged in the manner the bye-laws prescribe and the accounts must "
            "be open to members. A member may inspect the register, the minutes and the audited "
            "accounts, and demand copies on payment. "
            "Disputes between a member and the society go first to the Registrar of Cooperative "
            "Societies and then to the Cooperative Court in most States. Deficiency in service by "
            "the society can also found a consumer complaint, and residents of a RERA-registered "
            "project can approach the RERA authority against the builder for unfinished common areas."
        ),
        source_url=INDIA_CODE,
        topics=("housing society", "rwa", "maintenance", "cooperative", "apartment owners"),
        also_known_as=("resident welfare association", "society dues", "apartment association"),
    ),

    Passage(
        id="deposit_recovery",
        title="Getting your security deposit back from a landlord",
        act="Model Tenancy Act, 2021 and State Rent Acts; Limitation Act, 1963",
        section="Sections 11 and 21, Model Act; Article 55, Limitation Act",
        text=(
            "The deposit is your money held as security, not the landlord's income. Under the "
            "Model Tenancy Act it must be refunded when you hand back possession, after deducting "
            "only what the agreement allows — unpaid rent, unpaid utility bills, and the cost of "
            "damage beyond ordinary wear and tear. Repainting and routine cleaning are normally "
            "wear and tear, not damage, unless the agreement says otherwise. "
            "Protect yourself with evidence at both ends: dated photographs when you move in and "
            "when you leave, the final meter readings, and a written handover acknowledging that "
            "possession was returned. "
            "If the money is withheld, send a written demand by registered post giving a deadline "
            "and an account to pay into, and asking for an itemised account of any deduction. "
            "Where the State has adopted the Model Act, the Rent Authority decides deposit "
            "disputes and can order refund with interest. Elsewhere the remedy is a civil suit for "
            "recovery, usually before the Court of Small Causes, and the limitation period is three "
            "years from when the deposit became due. A landlord who simply keeps the money after "
            "being asked for it may also be answerable for criminal breach of trust, though courts "
            "treat an ordinary refund dispute as a civil matter."
        ),
        source_url=INDIA_CODE,
        topics=("security deposit", "deposit refund", "landlord not returning deposit",
                "advance rent", "wear and tear", "rent authority", "move out"),
        also_known_as=("deposit not returned", "landlord kept my deposit",
                       "get deposit back", "advance money refund"),
    ),

    # ── Money, banking and credit ───────────────────────────────────────
    Passage(
        id="loan_recovery_agents",
        title="What a recovery agent may and may not do",
        act="RBI Master Directions on Outsourcing and Fair Practices Code",
        section="RBI Fair Practices Code for Lenders; Bharatiya Nyaya Sanhita, 2023",
        text=(
            "A lender may employ recovery agents but remains answerable for what they do. RBI "
            "directions bar agents from calling before 8 a.m. or after 7 p.m., from using threats, "
            "abuse or public humiliation, from contacting your relatives, employer or neighbours "
            "about the debt, and from posting about it on social media. The borrower must be told "
            "the agent's identity and the details in writing before recovery is outsourced. "
            "Threatening or intimidating conduct is separately a criminal offence — criminal "
            "intimidation, trespass or extortion under the Bharatiya Nyaya Sanhita. "
            "Complain first to the lender's grievance officer, then to the RBI Ombudsman if there "
            "is no reply in thirty days, and to the police for threats. Secured assets can only be "
            "taken under the SARFAESI procedure with notice, not by force."
        ),
        source_url=RBI,
        topics=("recovery agent", "loan", "harassment", "rbi", "debt collection"),
        also_known_as=("collection agent", "loan harassment", "sarfaesi"),
    ),
    Passage(
        id="credit_score_dispute",
        title="Fixing a wrong entry on your credit report",
        act="Credit Information Companies (Regulation) Act, 2005",
        section="Sections 21 and 25; RBI directions of 2023",
        text=(
            "You are entitled to one free full credit report each calendar year from every credit "
            "information company. If an entry is wrong — a loan you never took, a settled account "
            "still shown as overdue, someone else's default against your PAN — you can demand "
            "correction under Section 21. "
            "The credit information company and the lender must resolve a dispute within thirty "
            "days. Since 2023 the RBI requires the lender to pay you a hundred rupees for each day "
            "of delay beyond that, and requires you to be told by SMS or email whenever your report "
            "is accessed or your data is updated. "
            "Escalate to the lender's nodal officer and then to the RBI Ombudsman. A wrong entry "
            "left uncorrected has also been treated as deficiency in service before consumer "
            "commissions."
        ),
        source_url=RBI,
        topics=("credit score", "cibil", "credit report", "dispute", "loan rejection"),
        also_known_as=("cibil score", "credit bureau", "experian"),
    ),
    Passage(
        id="digital_payment_fraud",
        title="If money leaves your account through UPI or a card",
        act="RBI Circular on Limiting Liability of Customers, 2017",
        section="Paragraphs 6–9",
        text=(
            "Your liability depends almost entirely on how fast you report. If the loss is due to "
            "the bank's own negligence or a system failure, you owe nothing whatever the delay. "
            "For a third-party fraud where neither you nor the bank is at fault, reporting within "
            "three working days means zero liability; four to seven working days caps your loss at "
            "between five thousand and twenty-five thousand rupees depending on the account type; "
            "beyond seven days the bank's own policy governs. "
            "The bank must credit the disputed amount within ten working days of your report and "
            "resolve the complaint within ninety days. Report on the bank's 24x7 number, insist on "
            "a written acknowledgement with a ticket number, and file on the National Cyber Crime "
            "Reporting Portal or the 1930 helpline — a report there within the golden hour can get "
            "the transfer frozen at the receiving bank. "
            "Sharing your own OTP or PIN moves the case into the negligence category, but that is "
            "for the bank to prove, not for you to disprove."
        ),
        source_url=RBI,
        topics=("upi fraud", "card fraud", "zero liability", "1930", "unauthorised transaction"),
        also_known_as=("otp fraud", "phishing", "cyber fraud money"),
    ),
    Passage(
        id="banking_ombudsman",
        title="Complaining about a bank, NBFC or payment app",
        act="Reserve Bank – Integrated Ombudsman Scheme, 2021",
        section="Clauses 9–11",
        text=(
            "One scheme now covers banks, NBFCs and payment system operators, with a single portal "
            "and no list of permitted grounds — any deficiency in service can be complained about. "
            "First complain to the institution itself. You may approach the Ombudsman if you get no "
            "reply within thirty days, or a reply you are not satisfied with, and you must do so "
            "within one year of that. "
            "Complain free of charge at cms.rbi.org.in, by email, or by post to the Centralised "
            "Receipt and Processing Centre in Chandigarh. No lawyer is needed. "
            "The Ombudsman can award the actual loss suffered, up to twenty lakh rupees, plus up to "
            "one lakh for the time, expense and mental anguish caused. An award you reject leaves "
            "your other remedies intact; consumer commissions and civil courts remain open."
        ),
        source_url=RBI,
        topics=("banking ombudsman", "bank complaint", "nbfc", "rbi", "deficiency in service"),
        also_known_as=("rbi ombudsman", "cms portal", "integrated ombudsman"),
    ),
    Passage(
        id="insurance_ombudsman",
        title="Escalating an insurance dispute without going to court",
        act="Insurance Ombudsman Rules, 2017",
        section="Rules 13–17",
        text=(
            "The Insurance Ombudsman handles delay in settling claims, partial or total repudiation, "
            "premium disputes, mis-selling, and policy servicing complaints against life, general "
            "and health insurers. "
            "Approach the insurer's grievance cell first. You may then go to the Ombudsman if there "
            "is no reply in thirty days or the reply is unsatisfactory, and you must do so within "
            "one year of the insurer's final reply. The claim must not exceed fifty lakh rupees and "
            "the same dispute must not be pending before a court or consumer commission. "
            "The process is free and no lawyer is required. An award is binding on the insurer, who "
            "must comply within thirty days; it is not binding on you, so refusing it leaves the "
            "consumer commission and the civil courts available."
        ),
        source_url="https://www.cioins.co.in",
        topics=("insurance ombudsman", "claim rejected", "repudiation", "mis-selling", "irdai"),
        also_known_as=("cioins", "insurance complaint", "irda ombudsman"),
    ),
    Passage(
        id="msme_delayed_payment",
        title="If a buyer will not pay a small business on time",
        act="Micro, Small and Medium Enterprises Development Act, 2006",
        section="Sections 15–18",
        text=(
            "A buyer must pay a registered micro or small enterprise within the agreed period, and "
            "in any case within forty-five days of accepting the goods or services. An agreement "
            "for a longer period is void to that extent. "
            "On default the buyer owes compound interest with monthly rests at three times the RBI "
            "bank rate, running from the due date. This is statutory and does not depend on the "
            "contract providing for interest. "
            "File before the Micro and Small Enterprises Facilitation Council of the State through "
            "the MSME Samadhaan portal. The Council first conciliates and then arbitrates, and must "
            "decide within ninety days. A buyer challenging the award has to deposit seventy-five "
            "per cent of it first, which is what gives the remedy its force. Udyam registration "
            "before the supply is what makes all of this available."
        ),
        source_url="https://samadhaan.msme.gov.in",
        topics=("msme", "delayed payment", "samadhaan", "interest", "small business"),
        also_known_as=("udyam", "msefc", "45 days payment"),
    ),

    # ── Work and wages ──────────────────────────────────────────────────
    Passage(
        id="provident_fund",
        title="Provident fund — what is deducted and how to get it out",
        act="Employees' Provident Funds and Miscellaneous Provisions Act, 1952",
        section="Sections 6 and 7A; EPF Scheme, 1952",
        text=(
            "The Act applies to establishments with twenty or more employees. Twelve per cent of "
            "basic wages plus dearness allowance is deducted from the employee and the employer "
            "contributes an equal amount, part of which goes to the pension scheme. "
            "The employer must deposit both shares by the fifteenth of the following month. "
            "Deducting an employee's share and not depositing it is not merely a default — it has "
            "been prosecuted as criminal breach of trust, and interest and damages are recoverable "
            "under Section 7Q and 14B. "
            "Check that deposits are actually being made through the UAN member passbook; do not "
            "rely on the payslip alone. The full balance can be withdrawn after two months of "
            "unemployment, and partial withdrawal is allowed for illness, housing, marriage and "
            "education. Complain on the EPFiGMS portal, then to the Regional PF Commissioner, who "
            "can hold an inquiry under Section 7A."
        ),
        source_url="https://www.epfindia.gov.in",
        topics=("provident fund", "epf", "uan", "withdrawal", "employer default"),
        also_known_as=("pf", "epfo", "employee provident fund"),
    ),
    Passage(
        id="esi_benefits",
        title="Medical cover and sickness pay through ESI",
        act="Employees' State Insurance Act, 1948",
        section="Sections 39, 46 and 85",
        text=(
            "ESI covers employees earning up to twenty-one thousand rupees a month — twenty-five "
            "thousand for those with a disability — in establishments with ten or more workers. "
            "The employee contributes 0.75 per cent of wages and the employer 3.25 per cent. "
            "Benefits are wider than most people realise: full medical care for the worker and the "
            "whole family with no ceiling on treatment cost, sickness benefit at about seventy per "
            "cent of wages for up to ninety-one days a year, maternity benefit for twenty-six "
            "weeks, disablement benefit at ninety per cent of wages, dependants' benefit on death "
            "from employment injury, and unemployment allowance under the Rajiv Gandhi Shramik "
            "Kalyan Yojana. "
            "An employer who deducts the contribution and does not pay it is punishable under "
            "Section 85. Complain to the Regional ESIC office or on the ESIC grievance portal."
        ),
        source_url="https://www.esic.gov.in",
        topics=("esi", "esic", "medical benefit", "sickness", "employment injury"),
        also_known_as=("employee state insurance", "esic card"),
    ),
    Passage(
        id="working_hours_overtime",
        title="Hours, rest and overtime pay",
        act="Factories Act, 1948 and Occupational Safety, Health and Working Conditions Code, 2020",
        section="Sections 51–59, Factories Act; State Shops and Establishments Acts",
        text=(
            "In a factory the limits are nine hours in a day and forty-eight in a week, with at "
            "least half an hour of rest after five hours of continuous work, a weekly holiday, and "
            "not more than ten and a half hours spread over the day. "
            "Work beyond nine hours a day or forty-eight a week must be paid at twice the ordinary "
            "rate. Overtime is capped — commonly fifty hours a quarter under the Factories Act, "
            "with higher State limits — and an employee cannot validly agree to give up the "
            "double-rate entitlement. "
            "Shops, offices and commercial establishments are governed by the State Shops and "
            "Establishments Act instead, which sets its own hours, closing times and leave. The "
            "OSH Code consolidates these but its provisions come into force as notified. "
            "Complain to the Labour Commissioner or the Inspector for the area."
        ),
        source_url=INDIA_CODE,
        topics=("working hours", "overtime", "double wages", "rest", "shops and establishments"),
        also_known_as=("48 hour week", "ot pay", "extra hours"),
    ),
    Passage(
        id="retrenchment_notice",
        title="Being laid off — notice, pay and order of selection",
        act="Industrial Disputes Act, 1947 and Industrial Relations Code, 2020",
        section="Sections 25F, 25G and 25N, Industrial Disputes Act",
        text=(
            "A workman who has completed one year of continuous service — 240 days in the preceding "
            "twelve months — cannot be retrenched without one month's written notice or wages in "
            "lieu, and compensation of fifteen days' average pay for every completed year of "
            "service. Notice must also go to the appropriate government. Retrenchment without these "
            "is void and reinstatement with back wages is a routine remedy. "
            "Section 25G requires last in, first out within a category unless there is a recorded "
            "reason to depart from it, and Section 25H gives retrenched workers preference if the "
            "employer hires again. "
            "In establishments with a hundred or more workers, prior government permission is "
            "needed under Section 25N; the Industrial Relations Code raises that threshold to three "
            "hundred. Disputes go to the Labour Court or Industrial Tribunal through the "
            "conciliation officer."
        ),
        source_url=INDIA_CODE,
        topics=("retrenchment", "layoff", "notice pay", "compensation", "reinstatement"),
        also_known_as=("termination", "downsizing", "last in first out"),
    ),
    Passage(
        id="gig_platform_workers",
        title="Where gig and platform workers stand",
        act="Code on Social Security, 2020",
        section="Sections 2(35), 2(61), 45 and 109–114",
        text=(
            "The Code recognises gig workers and platform workers as distinct categories for the "
            "first time, separate from 'employee'. That matters: the classic protections that ride "
            "on employment — provident fund, gratuity, retrenchment compensation, minimum wages — "
            "do not automatically follow, and platforms generally engage workers as independent "
            "contractors. "
            "What the Code does provide is a social security framework: registration on the "
            "e-Shram portal, a Social Security Fund, and aggregator contributions of one to two per "
            "cent of turnover subject to a five per cent cap on payments made to workers, funding "
            "life and disability cover, accident insurance, health and maternity benefits and old "
            "age protection. Schemes are framed by notification, so what is actually available "
            "depends on what has been notified. "
            "Some States have gone further with their own platform-worker legislation providing "
            "registration, a welfare board and a grievance mechanism."
        ),
        source_url=INDIA_CODE,
        topics=("gig worker", "platform worker", "e-shram", "aggregator", "social security"),
        also_known_as=("delivery partner", "cab driver", "freelancer rights"),
    ),
    Passage(
        id="bonded_labour",
        title="Forced and bonded labour",
        act="Bonded Labour System (Abolition) Act, 1976",
        section="Sections 4, 6 and 16; Article 23, Constitution",
        text=(
            "The bonded labour system stands abolished. Every bonded labourer is freed by force of "
            "law, and any obligation to repay a bonded debt is extinguished — the debt simply "
            "ceases to exist, and property taken as security must be returned. "
            "Compelling a person to work against a debt is punishable with up to three years' "
            "imprisonment and a fine. Forced labour also violates Article 23 of the Constitution, "
            "and the Supreme Court has held that paying less than the minimum wage amounts to "
            "forced labour. "
            "Release is ordered by the District Magistrate, who chairs the Vigilance Committee. "
            "Rehabilitation assistance under the central scheme runs from one lakh rupees to three "
            "lakh for the most vulnerable categories, and is not conditional on a conviction. "
            "Report to the District Magistrate, the Sub-Divisional Magistrate, the police, or the "
            "National Human Rights Commission."
        ),
        source_url=INDIA_CODE,
        topics=("bonded labour", "forced labour", "begar", "article 23", "rehabilitation"),
        also_known_as=("bandhua mazdoor", "debt bondage", "slavery"),
    ),

    # ── Health and education ────────────────────────────────────────────
    Passage(
        id="medical_negligence",
        title="When treatment goes wrong",
        act="Consumer Protection Act, 2019 and Bharatiya Nyaya Sanhita, 2023",
        section="Section 2(11) and Section 35, Consumer Protection Act; Section 106, BNS",
        text=(
            "Medical services for payment are 'services' under consumer law, so a patient can file "
            "a consumer complaint for deficiency. Free treatment at a wholly free hospital falls "
            "outside it. "
            "Negligence is not the same as an unsuccessful outcome. The test from Bolam, adopted in "
            "Jacob Mathew, is whether the doctor acted in accordance with a practice accepted as "
            "proper by a responsible body of practitioners in that field. An error of judgment by a "
            "competent professional is not negligence. "
            "Failure to obtain informed consent is a separate ground; consent for one procedure is "
            "not consent for another. "
            "Complaints go to the consumer commission by value, to the State Medical Council "
            "against the practitioner's registration, and in serious cases criminally under Section "
            "106 BNS — for which the Supreme Court requires gross negligence and a police "
            "investigation preceded by an independent medical opinion."
        ),
        source_url=INDIA_CODE,
        topics=("medical negligence", "doctor", "hospital", "consent", "compensation"),
        also_known_as=("wrong treatment", "surgery gone wrong", "jacob mathew"),
    ),
    Passage(
        id="patient_rights",
        title="What a hospital must tell you and may not withhold",
        act="Clinical Establishments (Registration and Regulation) Act, 2010 and "
            "NHRC Charter of Patients' Rights",
        section="Section 12; Charter of Patients' Rights, 2018",
        text=(
            "A patient is entitled to information about the illness, the proposed treatment and its "
            "risks, in a language they understand, and to a second opinion. Rates must be displayed "
            "and charged as displayed, and an itemised bill must be given. "
            "Records matter: a copy of case papers and investigation reports must be provided "
            "within twenty-four hours of a request, and the discharge summary or death summary on "
            "discharge. "
            "No hospital may refuse emergency care for want of payment or a police clearance — the "
            "Supreme Court settled this in Parmanand Katara — and a body cannot be detained over an "
            "unpaid bill. A woman is entitled to a female attendant during examination. "
            "Complain to the hospital's grievance officer, the State Clinical Establishments "
            "authority, the State Medical Council, or a consumer commission."
        ),
        source_url="https://nhrc.nic.in",
        topics=("patient rights", "hospital bill", "medical records", "emergency", "consent"),
        also_known_as=("charter of patients rights", "hospital refused treatment"),
    ),
    Passage(
        id="rte_admission",
        title="Free seats in private schools under the RTE quota",
        act="Right of Children to Free and Compulsory Education Act, 2009",
        section="Sections 12(1)(c), 13 and 16",
        text=(
            "Unaided private schools must reserve at least twenty-five per cent of entry-level "
            "seats for children from weaker sections and disadvantaged groups in the neighbourhood, "
            "and educate them free until Class VIII. The State reimburses the school at its own "
            "per-child expenditure or the school's fee, whichever is lower. "
            "No school may charge a capitation fee or screen the child or the parents in any "
            "selection process; where applications exceed seats the place is decided by lottery. "
            "Contravention attracts a fine of up to ten times the capitation fee. "
            "No child may be held back or expelled up to Class VIII, and no child may be denied "
            "admission for want of a transfer certificate or age proof. Apply through the State "
            "RTE portal in the admission window; complaints go to the local authority and then the "
            "State Commission for Protection of Child Rights."
        ),
        source_url=INDIA_CODE,
        topics=("rte", "school admission", "25 percent quota", "capitation fee", "free education"),
        also_known_as=("right to education quota", "ews admission", "school seat"),
    ),
    Passage(
        id="ragging",
        title="Ragging in a college or hostel",
        act="UGC Regulations on Curbing the Menace of Ragging, 2009",
        section="Regulations 3, 7 and 9",
        text=(
            "Ragging is defined widely: any conduct that teases, treats roughly, or raises fear or "
            "shame in a fresher, or asks them to do something they would not ordinarily do. It does "
            "not require physical contact and the victim's apparent consent is no defence. "
            "Punishments the institution may impose include suspension from classes, withholding "
            "results and scholarships, debarment from examinations, rustication and expulsion, "
            "along with a fine of up to twenty-five thousand rupees. Where the offenders cannot be "
            "identified, collective punishment of the group is permitted. "
            "Every institution must have an anti-ragging committee and squad and must obtain "
            "undertakings from students and parents each year. "
            "Report on the national helpline 1800-180-5522 or at antiragging.in, which forwards the "
            "complaint to the institution and the UGC. Serious incidents are also criminal offences "
            "— hurt, wrongful restraint, criminal intimidation or abetment of suicide."
        ),
        source_url="https://www.antiragging.in",
        topics=("ragging", "college", "hostel", "ugc", "student"),
        also_known_as=("hazing", "anti ragging helpline", "senior harassment"),
    ),

    # ── Marriage, children and the family ───────────────────────────────
    Passage(
        id="special_marriage_act",
        title="Marrying outside your religion, or without one",
        act="Special Marriage Act, 1954",
        section="Sections 4, 5, 6 and 15",
        text=(
            "The Special Marriage Act allows any two people to marry regardless of religion, and "
            "without either converting. The conditions are monogamy, sound mind and capacity to "
            "consent, and ages of twenty-one for the man and eighteen for the woman. "
            "Notice is given to the Marriage Officer of a district where one party has lived for at "
            "least thirty days. The notice is published and any person may object within thirty "
            "days on the ground that a condition is not met; an objection has to be inquired into "
            "and, if baseless, rejected. Courts have held that the couple's privacy must be "
            "respected and several High Courts have directed that notice not be sent to parents or "
            "displayed in a way that invites interference. "
            "Section 15 allows a couple already married under personal law to register under this "
            "Act. Succession for a marriage under this Act is generally governed by the Indian "
            "Succession Act, 1925."
        ),
        source_url=INDIA_CODE,
        topics=("special marriage", "interfaith", "court marriage", "notice", "registration"),
        also_known_as=("court marriage", "inter caste marriage", "civil marriage"),
    ),
    Passage(
        id="marriage_registration",
        title="Registering a marriage and why you need the certificate",
        act="Hindu Marriage Act, 1955 and Special Marriage Act, 1954",
        section="Section 8, Hindu Marriage Act; Sections 13 and 16, Special Marriage Act",
        text=(
            "The Supreme Court in Seema v. Ashwani Kumar directed all States to make registration "
            "of marriages compulsory, and every State now has rules for it. Registration does not "
            "make a marriage valid or invalid; it records a marriage that has already taken place. "
            "The certificate is what you will be asked for repeatedly — a spouse visa, a passport, "
            "a joint bank account or loan, a name change, insurance and pension nomination, and "
            "claims of inheritance or maintenance. "
            "Apply at the office of the Registrar of Marriages for the area where the marriage took "
            "place or where either party lives, with proof of age and address, wedding photographs "
            "or an invitation, and witnesses. A marriage under the Special Marriage Act is "
            "registered as part of the marriage itself."
        ),
        source_url=INDIA_CODE,
        topics=("marriage certificate", "registration", "proof of marriage", "visa", "passport"),
        also_known_as=("marriage registrar", "shaadi certificate"),
    ),
    Passage(
        id="child_custody",
        title="Who the child lives with after a separation",
        act="Guardians and Wards Act, 1890 and Hindu Minority and Guardianship Act, 1956",
        section="Section 17, Guardians and Wards Act; Section 6, HMGA",
        text=(
            "The governing consideration is the welfare of the child, and it overrides the "
            "statutory preference for any particular parent. Courts weigh the child's age, "
            "schooling, emotional ties and stability far above who earns more. The preference of a "
            "child old enough to form an intelligent view is considered but is not decisive. "
            "Custody of a child below five years is ordinarily given to the mother. The father is "
            "the natural guardian of a Hindu minor thereafter, with the mother taking that role "
            "after him — but the Supreme Court in Githa Hariharan read 'after' so that the mother "
            "can act as natural guardian where the father is absent or indifferent. "
            "Custody is not ownership. The parent who does not have custody keeps the right to "
            "visitation, and courts increasingly order shared parenting. Orders can be varied as "
            "circumstances change, and an interim arrangement can be sought while the case runs."
        ),
        source_url=INDIA_CODE,
        topics=("child custody", "guardian", "visitation", "welfare of child", "separation"),
        also_known_as=("custody battle", "guardianship", "parenting time"),
    ),
    Passage(
        id="adoption",
        title="Adopting a child lawfully",
        act="Juvenile Justice (Care and Protection of Children) Act, 2015 and "
            "Hindu Adoptions and Maintenance Act, 1956",
        section="Sections 56–65, JJ Act; Adoption Regulations, 2022",
        text=(
            "Adoption of a child in need of care and protection runs through CARA, the Central "
            "Adoption Resource Authority. Register on the CARINGS portal, complete a home study "
            "through a specialised adoption agency, and receive a referral by seniority. The court "
            "then passes an adoption order, which makes the child the adoptive parents' child for "
            "all purposes including inheritance. "
            "Any adoption of such a child outside this process is unlawful, and paying for a child "
            "is an offence. "
            "Hindus, Buddhists, Jains and Sikhs may alternatively adopt under the 1956 Act, which "
            "requires that the adopter not already have a living child of the same gender, and that "
            "there be at least twenty-one years between adopter and adoptee where they are of "
            "opposite sexes. Members of other communities may also adopt under the JJ Act, which "
            "is secular in application."
        ),
        source_url="https://cara.wcd.nic.in",
        topics=("adoption", "cara", "carings", "adoptive parents", "child care"),
        also_known_as=("adopt a child", "adoption agency", "godh"),
    ),
    Passage(
        id="live_in_relationship",
        title="Living together without marrying",
        act="Protection of Women from Domestic Violence Act, 2005",
        section="Section 2(f); Bharatiya Nagarik Suraksha Sanhita, 2023",
        text=(
            "A live-in relationship between consenting adults is not an offence. The Supreme Court "
            "in Lata Singh and again in Indra Sarma confirmed that two adults may live together, "
            "whatever society thinks of it. "
            "The Domestic Violence Act covers a 'relationship in the nature of marriage', so a "
            "woman in a live-in relationship can seek protection orders, residence orders, "
            "maintenance and compensation. Indra Sarma set out what qualifies — duration, a shared "
            "household, pooling of resources, and holding out to the world as a couple — and a "
            "relationship with a man the woman knows to be married generally does not. "
            "A child born of a live-in relationship is legitimate and inherits the parents' "
            "self-acquired property. Maintenance for the child stands independently of the parents' "
            "status. Some States now require registration of live-in relationships; the "
            "requirement is being tested in court."
        ),
        source_url=INDIA_CODE,
        topics=("live in relationship", "cohabitation", "domestic violence act", "legitimacy"),
        also_known_as=("living together", "partner rights", "unmarried couple"),
    ),
    Passage(
        id="child_marriage",
        title="Marriage below the legal age",
        act="Prohibition of Child Marriage Act, 2006",
        section="Sections 3, 9, 10 and 12",
        text=(
            "A marriage where the bride is under eighteen or the groom under twenty-one is "
            "voidable at the option of the party who was a child: they may seek a decree of nullity "
            "up to two years after attaining majority. Certain marriages are void outright — where "
            "the child was taken away, compelled, or trafficked. "
            "An adult man marrying a child, and anyone who performs, conducts, directs or abets a "
            "child marriage, faces up to two years' rigorous imprisonment and a fine of up to one "
            "lakh rupees. Parents and guardians who permit or fail to prevent it are punishable "
            "too. "
            "The wife is entitled to maintenance until she remarries, and custody of any child is "
            "decided on the child's welfare. Legitimacy of children born of such a marriage is "
            "preserved. "
            "Report to the Child Marriage Prohibition Officer, the District Magistrate, Childline "
            "on 1098, or the police; courts can injunct a marriage before it happens."
        ),
        source_url=INDIA_CODE,
        topics=("child marriage", "underage", "voidable", "1098", "prohibition officer",
                "marrying off a minor girl", "16 year old girl marriage",
                "family forcing marriage of a minor", "stop a wedding"),
        also_known_as=("bal vivah", "minor marriage", "underage girl being married off"),
    ),
    Passage(
        id="transgender_rights",
        title="Legal recognition of gender identity",
        act="Transgender Persons (Protection of Rights) Act, 2019",
        section="Sections 4–7, 9–13 and 18",
        text=(
            "A transgender person has a right to self-perceived gender identity. A certificate of "
            "identity is issued by the District Magistrate on application, without any medical "
            "examination; a revised certificate recording male or female follows gender-affirming "
            "surgery. NALSA v. Union of India recognised the third gender and the right to "
            "self-identification as part of Articles 14, 19 and 21. "
            "Discrimination is prohibited in education, employment, healthcare, access to goods and "
            "services, the right to movement, and the right to rent or occupy property. No child "
            "may be separated from their family on the ground of being transgender, except by court "
            "order in the child's interest. "
            "Offences including forced labour, denial of access to a public place, and physical, "
            "sexual, verbal or economic abuse carry six months to two years' imprisonment with a "
            "fine. Complaints go to the National Council for Transgender Persons and the complaint "
            "officer each establishment must designate."
        ),
        source_url=INDIA_CODE,
        topics=("transgender", "gender identity", "nalsa judgment", "discrimination", "certificate"),
        also_known_as=("third gender", "trans rights", "gender change"),
    ),
    Passage(
        id="one_stop_centre",
        title="Immediate help for a woman facing violence",
        act="Ministry of Women and Child Development scheme; "
            "Protection of Women from Domestic Violence Act, 2005",
        section="One Stop Centre Scheme; Section 9, PWDVA",
        text=(
            "One Stop Centres — Sakhi Centres — bring police assistance, medical aid, legal aid and "
            "counselling together in one place, usually at or near a district hospital, and provide "
            "temporary shelter for up to five days. Support is free and available regardless of "
            "whether the woman wants to file a case. "
            "The women's helpline 181 connects to the nearest centre, and 112 is the emergency "
            "number. Childline 1098 handles a child at risk. "
            "A Protection Officer appointed under the Domestic Violence Act in each district must "
            "help file a Domestic Incident Report, arrange medical examination and shelter, and "
            "assist in approaching the Magistrate — and can be approached directly, without a "
            "lawyer and without going to the police first. Relief under that Act includes a "
            "protection order, the right to stay in the shared household, maintenance and custody, "
            "and the Magistrate is expected to decide within sixty days."
        ),
        source_url="https://wcd.gov.in",
        topics=("one stop centre", "sakhi", "181", "protection officer", "shelter"),
        also_known_as=("women helpline", "domestic incident report", "sakhi centre"),
    ),

    # ── Criminal law people actually meet ───────────────────────────────
    Passage(
        id="cheating_offence",
        title="Cheating — being tricked out of money or property",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Sections 316–318",
        text=(
            "Cheating is deceiving someone into delivering property or doing something they would "
            "not otherwise have done. The critical element is dishonest intention *at the time of "
            "the promise*. A person who genuinely intended to perform and then failed has committed "
            "a breach of contract, not an offence, and courts regularly quash criminal cases that "
            "are really civil disputes dressed up. "
            "Simple cheating carries up to three years. Cheating with delivery of property, the "
            "common charge in investment and property frauds, carries up to seven years and is "
            "cognizable and non-bailable — this is the old Section 420 IPC. Cheating by "
            "personation is dealt with separately, as is criminal breach of trust under Section "
            "316, which applies where property was entrusted to the accused and then misapplied. "
            "File an FIR at the police station where the deception or the loss occurred; online "
            "frauds may be reported on the cybercrime portal or 1930."
        ),
        source_url=INDIA_CODE,
        topics=("cheating", "fraud", "420", "breach of trust", "dishonest intention",
                "took my money and disappeared", "promised and vanished",
                "conned out of money", "duped"),
        also_known_as=("section 420", "dhokha", "criminal breach of trust",
                       "took my money and vanished", "cheated me of money"),
    ),
    Passage(
        id="notice_instead_of_arrest",
        title="A notice to appear instead of being arrested",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 35(3)–(6)",
        text=(
            "Where the offence carries less than seven years' imprisonment, the police must issue a "
            "notice to appear rather than arrest, unless arrest is necessary for a recorded reason "
            "— preventing further offence, proper investigation, stopping evidence being tampered "
            "with, or securing the person's presence. This is the old Section 41A CrPC, and "
            "Arnesh Kumar v. State of Bihar made the safeguards binding, with departmental action "
            "against officers who ignore them. "
            "A person who receives the notice must attend as required. Someone who complies cannot "
            "be arrested unless the officer records reasons why arrest has become necessary. "
            "Keep the notice, attend, and take a lawyer. If arrest follows despite compliance, the "
            "recorded reasons can be challenged before the Magistrate, and the failure to follow "
            "Arnesh Kumar is a strong ground for bail."
        ),
        source_url=INDIA_CODE,
        topics=("notice to appear", "arnesh kumar", "arrest", "41a", "police notice"),
        also_known_as=("section 41a crpc", "41a notice", "bnss 35"),
    ),
    Passage(
        id="victim_compensation",
        title="Compensation for a victim of crime",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023 and State Victim Compensation Schemes",
        section="Sections 396 and 397, BNSS; NALSA Compensation Scheme for Women Victims",
        text=(
            "Every State runs a Victim Compensation Scheme funded independently of the accused. "
            "Compensation does not depend on a conviction, and can be awarded even where the "
            "offender is not traced or is acquitted. "
            "The court may recommend compensation, or the victim may apply directly to the State or "
            "District Legal Services Authority. Interim relief can be ordered for immediate medical "
            "treatment, and Section 397 requires hospitals to treat victims of acid attack, rape "
            "and certain other offences free of cost. "
            "The NALSA scheme sets indicative minimums for women victims — substantial sums for "
            "acid attack, rape and loss of life, with more for a victim who is a minor. Apply "
            "through the DLSA in the district; free legal aid covers the application, and a victim "
            "of a serious offence is entitled to legal aid regardless of income."
        ),
        source_url="https://nalsa.gov.in",
        topics=("victim compensation", "dlsa", "acid attack", "free treatment", "nalsa scheme"),
        also_known_as=("compensation scheme", "victim relief"),
    ),
    Passage(
        id="acid_attack",
        title="Acid attacks — offence, treatment and compensation",
        act="Bharatiya Nyaya Sanhita, 2023",
        section="Sections 124 and 397, BNSS; Laxmi v. Union of India",
        text=(
            "Causing grievous hurt by acid carries a minimum of ten years, extendable to "
            "imprisonment for life, with a fine payable to the victim sufficient to meet medical "
            "expenses. Attempting to throw acid carries five to seven years. "
            "Following Laxmi v. Union of India, the retail sale of acid is regulated: sellers must "
            "record the buyer's identity and the quantity, sales to those under eighteen are "
            "prohibited, and stocks must be declared. "
            "Treatment must be free at every hospital, private or government, including "
            "reconstructive surgery, and no hospital may refuse first aid for want of payment or "
            "police formalities. Refusal is itself an offence. "
            "Victims are entitled to compensation of at least three lakh rupees under the State "
            "scheme, and acid attack survivors with disfigurement are recognised as persons with "
            "disability under the 2016 Act, which brings reservation and pension entitlements."
        ),
        source_url=INDIA_CODE,
        topics=("acid attack", "grievous hurt", "laxmi judgment", "free treatment", "disability"),
        also_known_as=("tezaab", "acid sale rules"),
    ),
    Passage(
        id="human_trafficking",
        title="Trafficking of persons",
        act="Bharatiya Nyaya Sanhita, 2023 and Immoral Traffic (Prevention) Act, 1956",
        section="Sections 143–144, BNS; Article 23, Constitution",
        text=(
            "Trafficking is recruiting, transporting, harbouring or receiving a person by threat, "
            "force, abduction, fraud, deception, abuse of power or inducement, for the purpose of "
            "exploitation. Consent of the victim is irrelevant where any of those means is used. "
            "Exploitation includes sexual exploitation, slavery, servitude and forced removal of "
            "organs. "
            "The base offence carries seven to ten years. Trafficking of a child carries ten years "
            "to life, and of more than one child, life imprisonment. A public servant or police "
            "officer involved faces imprisonment for life. "
            "The victim is not to be prosecuted; a trafficked person found in commercial sexual "
            "exploitation is to be treated as a victim requiring rehabilitation. "
            "Report to the police, the Anti Human Trafficking Unit in the district, Childline 1098 "
            "for a child, or the NHRC. Victim compensation and free legal aid are available."
        ),
        source_url=INDIA_CODE,
        topics=("trafficking", "exploitation", "forced prostitution", "ahtu", "child trafficking",
                "taken away for work and never returned", "lured with a job offer",
                "girl taken from the village", "missing after being promised work"),
        also_known_as=("human trafficking", "immoral traffic", "bonded sex work",
                       "taken away for work", "sold into work"),
    ),

    # ── Everyday services ───────────────────────────────────────────────
    Passage(
        id="telecom_complaint",
        title="Complaints about a phone or broadband connection",
        act="TRAI Telecom Consumers Protection Regulations, 2012 and "
            "Telecom Consumers Complaint Redressal Regulations, 2012",
        section="Regulations 3–8",
        text=(
            "Every operator must run a toll-free consumer care number and a web-based docket "
            "system. Complaints are registered with a docket number, which the operator must give "
            "you — insist on it, because escalation depends on it. Billing complaints must be "
            "resolved in four weeks and service complaints in three days for most categories. "
            "If unresolved, escalate to the operator's appellate authority, whose details must be "
            "published on the website and bills, within thirty days of the docket closing. The "
            "appellate authority must decide in thirty-nine days. "
            "TRAI itself does not adjudicate individual complaints, so the remedy after that is a "
            "consumer commission. "
            "Unwanted commercial calls and messages are handled separately: register your "
            "preference on the DND service or the TRAI DND app, and report violations there — "
            "operators face financial disincentives for unregistered telemarketers."
        ),
        source_url="https://www.trai.gov.in",
        topics=("telecom", "trai", "mobile bill", "broadband", "dnd", "spam calls"),
        also_known_as=("network problem", "sim complaint", "do not disturb"),
    ),
    Passage(
        id="electricity_complaint",
        title="Power cuts, wrong bills and new connections",
        act="Electricity Act, 2003",
        section="Sections 42(5), 43, 56 and 57",
        text=(
            "Every distribution licensee must have a Consumer Grievance Redressal Forum, and above "
            "it an Electricity Ombudsman appointed by the State Regulatory Commission. Approach the "
            "Forum first; the Ombudsman hears you if you are dissatisfied with its order. "
            "A licensee must supply on application within one month of the requisition under "
            "Section 43, and Standards of Performance notified by the State Commission fix "
            "timelines for restoring supply, replacing a meter and correcting a bill — with "
            "compensation payable automatically for breach in many States. "
            "Section 56 is worth knowing: supply cannot be cut without fifteen clear days' written "
            "notice, and no arrear can be recovered after two years from when it first became due "
            "unless it was shown continuously as recoverable. "
            "Theft of electricity under Section 135 is a separate criminal matter dealt with by "
            "Special Courts, not by the consumer forum."
        ),
        source_url=INDIA_CODE,
        topics=("electricity", "power cut", "wrong bill", "ombudsman", "new connection"),
        also_known_as=("bijli", "discom complaint", "meter problem"),
    ),
    Passage(
        id="railway_passenger_rights",
        title="Refunds and compensation on the railways",
        act="Railways Act, 1989 and Railway Passengers (Cancellation of Tickets and "
            "Refund of Fare) Rules, 2015",
        section="Sections 124, 124A and 125; Refund Rules 4–11",
        text=(
            "If a train is delayed by more than three hours you may cancel and claim a full refund. "
            "If the train is cancelled, the refund is automatic for e-tickets. Where a confirmed "
            "berth in the class booked is not provided, the difference is refundable. "
            "Section 124A provides compensation for death or injury in an untoward incident "
            "regardless of anyone's negligence — it is a no-fault liability, and claims go to the "
            "Railway Claims Tribunal, not a civil court. Applications should be made without undue "
            "delay and the Tribunal can condone delay for good reason. "
            "Deficiency in service — a filthy coach, missing bedding, catering overcharging — has "
            "been held to found a consumer complaint against the Railways. "
            "Complain on RailMadad (139 or railmadad.indianrailways.gov.in), which is tracked and "
            "time-bound, before going to a consumer commission."
        ),
        source_url="https://railmadad.indianrailways.gov.in",
        topics=("railway", "train delay", "refund", "claims tribunal", "railmadad"),
        also_known_as=("irctc refund", "train cancelled", "tdr"),
    ),
    Passage(
        id="airline_passenger_rights",
        title="Denied boarding, cancellation and delay on a flight",
        act="DGCA Civil Aviation Requirements, Section 3, Series M, Part IV",
        section="CAR Part IV, paragraphs 3–4",
        text=(
            "If you are denied boarding because the flight was overbooked and the airline can put "
            "you on an alternate flight within one hour, nothing is payable. Otherwise compensation "
            "is due — broadly, an amount tied to the one-way fare plus airline fuel charge, rising "
            "with the length of the delay to the alternate flight, subject to caps set in the CAR. "
            "For a cancellation notified less than two weeks ahead, the airline must either refund "
            "the full fare or provide an alternate flight, and pay compensation where the "
            "notification was too late or the alternate does not fit the prescribed window. "
            "For delays the airline must provide meals and refreshments, and hotel accommodation "
            "where an overnight stay becomes necessary; if the delay exceeds six hours you must be "
            "offered an alternate flight or a full refund. "
            "None of this applies where the cause is outside the airline's control — weather, "
            "political instability, security risk or air traffic control. Escalate on the AirSewa "
            "portal, then to a consumer commission."
        ),
        source_url="https://www.dgca.gov.in",
        topics=("flight delay", "cancellation", "denied boarding", "dgca", "airsewa"),
        also_known_as=("airline compensation", "overbooking", "flight refund"),
    ),

    # ── Civic life, identity and welfare ────────────────────────────────
    Passage(
        id="birth_death_certificate",
        title="Getting a birth or death certificate, including a late one",
        act="Registration of Births and Deaths Act, 1969 (amended 2023)",
        section="Sections 8, 13 and 17",
        text=(
            "Births and deaths must be reported within twenty-one days. Registration in that window "
            "is free of charge. "
            "Late registration is still possible: up to thirty days on payment of a late fee; up to "
            "one year with the written permission of the prescribed authority and an affidavit; and "
            "after one year only on the order of a Magistrate, with an affidavit and supporting "
            "evidence such as hospital or school records. "
            "The 2023 amendment makes the birth certificate the single document for proving date "
            "and place of birth for admission, a driving licence, a passport, Aadhaar, marriage "
            "registration and government employment, for those born after the amendment came into "
            "force. It also provides for a national database and for digital delivery of "
            "certificates. "
            "Apply at the local registrar — municipal body or panchayat — or through the State "
            "portal on the CRS system. A correction of an entry is made under Section 15."
        ),
        source_url=INDIA_CODE,
        topics=("birth certificate", "death certificate", "late registration", "crs", "correction"),
        also_known_as=("janam praman patra", "delayed registration"),
    ),
    Passage(
        id="caste_income_certificate",
        title="Caste, income and domicile certificates",
        act="State revenue rules; Constitution of India",
        section="Articles 15(4) and 16(4); State notifications",
        text=(
            "These certificates are issued by the revenue administration — usually the Tehsildar, "
            "SDM or District Magistrate — and are needed for reservation in education and public "
            "employment, scholarships, fee concessions and most welfare schemes. "
            "A caste certificate for SC or ST is issued on proof of the caste of the father or, "
            "where permitted, another blood relative in the paternal line, together with proof of "
            "residence. It is issued in the State where the caste is notified; a caste scheduled in "
            "one State does not automatically carry to another. An income certificate is based on "
            "the family's income from all sources for the relevant financial year. An OBC "
            "non-creamy-layer certificate has a validity period and must be renewed. "
            "Most States accept applications online with a prescribed disposal time; delay can be "
            "pursued under the State public services guarantee legislation, which many States have, "
            "and refusal is appealable to the Collector."
        ),
        source_url=INDIA_CODE,
        topics=("caste certificate", "income certificate", "domicile", "reservation", "obc"),
        also_known_as=("jati praman patra", "non creamy layer", "residence certificate"),
    ),
    Passage(
        id="aadhaar_rights",
        title="What Aadhaar can and cannot be demanded for",
        act="Aadhaar (Targeted Delivery of Financial and Other Subsidies, Benefits and "
            "Services) Act, 2016",
        section="Sections 7 and 57; Justice K.S. Puttaswamy (Aadhaar) v. Union of India",
        text=(
            "The Supreme Court upheld Aadhaar for subsidies, benefits and services funded from the "
            "Consolidated Fund of India, and for income tax and PAN. It struck down Section 57, so "
            "private companies cannot demand Aadhaar for a contract, and it held that Aadhaar "
            "cannot be made mandatory for a bank account, a mobile connection, or school admission. "
            "Crucially, no benefit may be denied for want of authentication. Where biometrics fail "
            "— worn fingerprints are common among manual workers — an alternative means of "
            "identification must be offered, and the Court was explicit that no child or entitled "
            "person may be excluded from rations, pensions or schooling on this ground. "
            "Enrolment and updating are free for the mandated updates. You can lock biometrics, "
            "use a Virtual ID instead of the number, and see the authentication history on the UIDAI "
            "portal. Complaints go to UIDAI on 1947."
        ),
        source_url="https://uidai.gov.in",
        topics=("aadhaar", "uidai", "authentication", "puttaswamy", "mandatory"),
        also_known_as=("aadhar card", "biometric failure", "virtual id"),
    ),
    Passage(
        id="mgnrega_work",
        title="The right to a hundred days of paid work",
        act="Mahatma Gandhi National Rural Employment Guarantee Act, 2005",
        section="Sections 3 and 7; Schedule II",
        text=(
            "Every rural household whose adult members volunteer for unskilled manual work is "
            "entitled to at least a hundred days of wage employment in a financial year. "
            "Apply for a job card at the gram panchayat; it must be issued within fifteen days and "
            "is free. On a written application for work, employment must be provided within fifteen "
            "days, and within five kilometres of the village — beyond that, an extra ten per cent "
            "of the wage is payable for travel and living expenses. "
            "If work is not provided in fifteen days, an unemployment allowance becomes payable by "
            "the State. Wages must be paid within fifteen days of the close of the muster period, "
            "directly into the worker's account, and delay attracts compensation. "
            "At least a third of beneficiaries are to be women, and equal wages are payable "
            "regardless of gender. Worksite facilities — drinking water, shade, first aid, and "
            "crèche where there are young children — are mandatory. Complaints go to the Programme "
            "Officer and the District Programme Coordinator, and social audits are compulsory."
        ),
        source_url="https://nrega.nic.in",
        topics=("mgnrega", "job card", "rural employment", "unemployment allowance", "wages"),
        also_known_as=("nrega", "100 days work", "narega"),
    ),
    Passage(
        id="street_vendor_rights",
        title="Street vendors and eviction",
        act="Street Vendors (Protection of Livelihood and Regulation of Street Vending) Act, 2014",
        section="Sections 3, 18, 19 and 27",
        text=(
            "A vendor identified in the survey conducted by the Town Vending Committee cannot be "
            "evicted or have goods confiscated until the survey is completed and a certificate of "
            "vending is issued or refused. "
            "Where relocation or eviction is necessary, thirty days' notice is required. Goods "
            "seized must be returned within two working days on payment of the prescribed fee, and "
            "perishables must be dealt with the same day. "
            "Vending is regulated, not prohibited: the Town Vending Committee — on which at least "
            "forty per cent of members are vendors and a third of those women — decides vending "
            "zones and the holding capacity. Section 27 overrides other laws, so a municipal "
            "bye-law cannot be used to remove a vendor with a certificate. "
            "Disputes go to the Grievance Redressal Committee chaired by a civil judge or judicial "
            "magistrate. A vendor may also approach the High Court, and the Supreme Court has "
            "recognised street vending as part of the Article 19(1)(g) right to trade."
        ),
        source_url=INDIA_CODE,
        topics=("street vendor", "hawker", "eviction", "town vending committee", "livelihood"),
        also_known_as=("rehri patri", "footpath shop", "vending certificate"),
    ),

    # ── Personal law beyond the Hindu statutes ──────────────────────────
    Passage(
        id="muslim_divorce_maintenance",
        title="Divorce and maintenance under Muslim personal law",
        act="Muslim Personal Law (Shariat) Application Act, 1937; Muslim Women "
            "(Protection of Rights on Marriage) Act, 2019",
        section="Sections 3–4 of the 2019 Act; Shayara Bano v. Union of India",
        text=(
            "Instant triple talaq — talaq-e-biddat, pronounced three times at once — was held void "
            "and unconstitutional in Shayara Bano, and the 2019 Act makes pronouncing it an "
            "offence punishable with up to three years. The marriage is not dissolved by it. Other "
            "forms of talaq that allow a period for reconciliation remain lawful, as do khula "
            "(divorce at the wife's instance) and mubarat (by mutual consent). A wife may also "
            "seek judicial divorce under the Dissolution of Muslim Marriages Act, 1939 on grounds "
            "including cruelty, desertion, failure to maintain, and the husband's imprisonment. "
            "Mehr (dower) is the wife's absolute property and is recoverable as a debt. "
            "On maintenance, Shah Bano and later Danial Latifi held that a divorced Muslim woman "
            "is entitled to a reasonable and fair provision extending beyond the iddat period, and "
            "the Supreme Court has confirmed she may also claim under the general maintenance "
            "provision available to women of every religion. The 2019 Act separately entitles her "
            "to a subsistence allowance and custody of minor children."
        ),
        source_url=INDIA_CODE,
        topics=("triple talaq", "muslim divorce", "mehr", "iddat", "khula",
                "muslim woman maintenance"),
        also_known_as=("talaq", "shayara bano", "danial latifi", "dower"),
    ),

    # ── Wages and the unorganised worker ────────────────────────────────
    Passage(
        id="minimum_wages",
        title="Minimum wages and being paid less than one",
        act="Code on Wages, 2019",
        section="Sections 5–9 and 45; Minimum Wages Act, 1948",
        text=(
            "A minimum wage is a floor, not a target. Paying below it is unlawful even if the "
            "worker agreed, because the agreement is void to that extent — and the Supreme Court "
            "has held that exacting labour below the minimum wage amounts to forced labour under "
            "Article 23. "
            "Rates are fixed by the appropriate government by category of employment, skill level "
            "and area, and are revised periodically; a national floor wage sets a level below which "
            "no State may fix its rate. The Code extends minimum wages to all employment, organised "
            "and unorganised alike, rather than only to scheduled employments as before. "
            "Wages must be paid by the seventh day after the wage period for smaller "
            "establishments, and deductions are limited to those the Code permits and capped at "
            "fifty per cent of wages. "
            "Claim unpaid or underpaid wages before the authority appointed under the Code; there "
            "is no court fee, the limitation period is three years, and the authority can order up "
            "to ten times the claim as compensation."
        ),
        source_url=INDIA_CODE,
        topics=("minimum wage", "underpaid", "wage floor", "deductions", "unorganised"),
        also_known_as=("paid below minimum wage", "wage board", "national floor wage"),
    ),
    Passage(
        id="eshram_unorganised",
        title="Registering as an unorganised worker",
        act="Code on Social Security, 2020; Unorganised Workers' Social Security Act, 2008",
        section="Sections 112–113, Code on Social Security",
        text=(
            "Most of India's workforce is unorganised — construction labour, domestic workers, "
            "street vendors, agricultural labour, drivers, self-employed artisans — and outside "
            "provident fund and ESI. e-Shram is the national database that connects them to "
            "welfare schemes. "
            "Registration is free and self-service, needing an Aadhaar-linked mobile number and a "
            "bank account, and is open to workers aged sixteen to fifty-nine who are not income tax "
            "payers and not members of EPFO or ESIC. It issues a Universal Account Number valid "
            "across States, which matters for migrant workers whose entitlements otherwise lapse "
            "when they move. "
            "Registration brings accident insurance cover and is used as the eligibility list for "
            "ration portability, pension schemes and State welfare boards. "
            "Building and construction workers should additionally register with the State Building "
            "and Other Construction Workers Welfare Board, which runs its own cess-funded benefits "
            "for education, maternity, housing and disability."
        ),
        source_url="https://eshram.gov.in",
        topics=("e-shram", "unorganised worker", "uan", "migrant worker", "welfare board"),
        also_known_as=("eshram card", "construction worker board", "domestic worker"),
    ),

    # ── Health, welfare and identity ────────────────────────────────────
    Passage(
        id="disability_certificate",
        title="Getting a disability certificate and UDID card",
        act="Rights of Persons with Disabilities Act, 2016",
        section="Sections 56–58; RPwD Rules, 2017",
        text=(
            "Benefits under the Act — four per cent reservation in government employment, five per "
            "cent in higher education, scholarships, travel concessions, income tax relief and "
            "pension — all run off a certificate of disability. "
            "It is issued by a medical authority notified by the State, usually a board at the "
            "district hospital, on application with proof of identity and residence. The Act "
            "recognises twenty-one specified disabilities, including several added in 2016 such as "
            "learning disability, autism, thalassaemia and acid-attack disfigurement. "
            "Where the disability is assessed at forty per cent or more the person qualifies as a "
            "'person with benchmark disability', which is the threshold for reservation. A "
            "certificate for a permanent condition is issued for life; otherwise it is reissued on "
            "reassessment. "
            "Apply through the UDID portal, which issues a single card usable across States. "
            "Refusal or delay is appealable to the district authority, and grievances go to the "
            "State Commissioner for Persons with Disabilities."
        ),
        source_url="https://www.swavlambancard.gov.in",
        topics=("disability certificate", "udid", "benchmark disability", "reservation",
                "rpwd"),
        also_known_as=("handicapped certificate", "divyang card", "40 percent disability"),
    ),
    Passage(
        id="ayushman_bharat",
        title="Free hospital treatment under Ayushman Bharat",
        act="Ayushman Bharat Pradhan Mantri Jan Arogya Yojana",
        section="Scheme guidelines, National Health Authority",
        text=(
            "The scheme provides cashless secondary and tertiary hospital care up to five lakh "
            "rupees per family per year at empanelled public and private hospitals. There is no cap "
            "on family size or age, and pre-existing conditions are covered from day one. "
            "Eligibility is based on the deprivation criteria of the Socio-Economic Caste Census "
            "rather than an application, so a household is either on the list or not; several "
            "States have extended cover to additional groups, and citizens aged seventy and above "
            "are covered irrespective of income under a later extension. "
            "Cover includes pre-hospitalisation for three days and post-hospitalisation for fifteen "
            "days, with medicines and diagnostics. "
            "An empanelled hospital may not demand payment for a covered procedure, and doing so is "
            "a ground for action against the empanelment. Check eligibility and find hospitals on "
            "the PMJAY portal or through the Ayushman Mitra desk at the hospital; complaints go to "
            "the State Health Agency or the 14555 helpline."
        ),
        source_url="https://pmjay.gov.in",
        topics=("ayushman bharat", "pmjay", "free treatment", "health insurance", "hospital"),
        also_known_as=("ayushman card", "jan arogya", "5 lakh health cover"),
    ),

    # ── Criminal procedure people ask about ─────────────────────────────
    Passage(
        id="sextortion_online",
        title="Blackmail with intimate images or video calls",
        act="Bharatiya Nyaya Sanhita, 2023 and Information Technology Act, 2000",
        section="Sections 308 and 351, BNS; Sections 66E and 67 of the IT Act",
        text=(
            "The common pattern is a stranger initiating a video call, recording it, and demanding "
            "money to stop it being sent to your contacts. This is extortion and criminal "
            "intimidation, and capturing or publishing images of a private area without consent is "
            "separately an offence. "
            "Do not pay. Payment funds the next demand and is followed by further demands in almost "
            "every reported case. Do not delete anything: keep the profile link, the chat, the "
            "payment demand and the numbers used, because that is the evidence. Block the account "
            "afterwards and restrict who can see your contact list. "
            "Report immediately on the National Cyber Crime Reporting Portal or the 1930 helpline. "
            "Reporting within the golden hour lets the receiving account be frozen. A complaint can "
            "be filed anonymously, and the portal has a dedicated route for women and children. "
            "The victim of this offence has committed none. Courts and police guidance treat the "
            "person targeted as a complainant, and the platform must remove impersonating or "
            "intimate content within twenty-four hours of being told."
        ),
        source_url=INDIA_CODE,
        topics=("sextortion", "blackmail", "video call scam", "1930", "intimate images"),
        also_known_as=("nude video call blackmail", "cyber blackmail", "honey trap"),
    ),
    Passage(
        id="fir_quashing",
        title="Getting a false or settled criminal case ended",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 528, BNSS; State of Haryana v. Bhajan Lal",
        text=(
            "A High Court has inherent power to quash an FIR or a criminal proceeding to prevent "
            "abuse of process. Bhajan Lal sets out the categories where this is appropriate: the "
            "allegations, taken at face value, disclose no offence; they are absurd or inherently "
            "improbable; the proceeding is manifestly attended with mala fides or is instituted "
            "with an ulterior motive; or there is a legal bar to prosecution. "
            "The court does not weigh evidence or decide who is telling the truth at this stage; it "
            "reads the complaint as it stands. "
            "A separate and very common route is quashing on settlement. Where the dispute is "
            "essentially private — matrimonial, commercial, a property quarrel — the High Court may "
            "quash even a non-compoundable offence if the parties have genuinely settled, following "
            "Gian Singh. That discretion is not available for grave offences against society such "
            "as murder, rape or corruption, however willing the complainant. "
            "Free legal aid covers a quashing petition for anyone eligible under the Legal Services "
            "Authorities Act."
        ),
        source_url=INDIA_CODE,
        topics=("quash fir", "false case", "482", "settlement", "high court"),
        also_known_as=("section 482 crpc", "quashing petition", "bhajan lal", "gian singh"),
    ),
    Passage(
        id="compounding_offences",
        title="Settling a criminal case with the complainant",
        act="Bharatiya Nagarik Suraksha Sanhita, 2023",
        section="Section 359 and the First Schedule, BNSS",
        text=(
            "Some offences may be compounded — settled with the person wronged, ending the case in "
            "an acquittal. The schedule lists which, and divides them in two: those the parties may "
            "compound themselves, such as simple hurt, criminal trespass, defamation and criminal "
            "breach of contract of service; and those needing the court's permission, such as "
            "grievous hurt, theft and criminal breach of trust. "
            "Everything not listed is non-compoundable and cannot be settled this way, whatever the "
            "complainant wants — though a High Court may still quash on settlement where the "
            "dispute is essentially private. "
            "Compounding must be the complainant's free choice; a compromise obtained by pressure "
            "can be set aside. Once permitted, compounding has the effect of an acquittal. "
            "After conviction, compounding requires the leave of the court hearing the appeal. Lok "
            "Adalats routinely dispose of compoundable cases, and the court fee is refunded."
        ),
        source_url=INDIA_CODE,
        topics=("compounding", "settlement", "compoundable offence", "acquittal", "compromise"),
        also_known_as=("compromise in criminal case", "settle a case", "section 320 crpc"),
    ),

    # ── Land, farming and civic entitlement ─────────────────────────────
    Passage(
        id="crop_insurance",
        title="Crop insurance and a rejected claim",
        act="Pradhan Mantri Fasal Bima Yojana",
        section="Operational Guidelines, Ministry of Agriculture",
        text=(
            "Premium payable by the farmer is capped at two per cent of the sum insured for kharif "
            "food and oilseed crops, one and a half per cent for rabi, and five per cent for "
            "commercial and horticultural crops; the governments pay the balance. Enrolment is "
            "voluntary for all farmers, including tenants and sharecroppers, who need proof of an "
            "insurable interest in the land. "
            "Cover runs from prevented sowing through standing-crop loss to post-harvest losses for "
            "a limited period, and includes localised calamities such as hailstorm, landslide and "
            "inundation. "
            "Timing is what most claims turn on: an individual loss must be reported within "
            "seventy-two hours, through the crop insurance app, the bank, the insurer's toll-free "
            "number or the agriculture department. Claims are otherwise assessed on area-based crop "
            "cutting experiments rather than individual inspection. "
            "A rejected or delayed claim goes to the District Level Grievance Committee and then "
            "the State Level Committee; insurers owe interest for settlement delayed beyond the "
            "prescribed period."
        ),
        source_url="https://pmfby.gov.in",
        topics=("crop insurance", "pmfby", "farmer", "claim rejected", "crop loss"),
        also_known_as=("fasal bima", "kisan insurance", "72 hours crop loss"),
    ),
    Passage(
        id="land_records",
        title="Land records, and correcting a wrong entry",
        act="State land revenue codes; Digital India Land Records Modernisation Programme",
        section="Varies by State",
        text=(
            "The record of rights — variously khatauni, 7/12 extract, pahani, RTC, jamabandi — "
            "shows who is recorded as holding the land, its extent, and the crops and encumbrances "
            "noted on it. Most States publish it online through the Bhulekh or equivalent portal, "
            "along with the cadastral map and mutation status. "
            "The record is presumptive evidence of possession, not conclusive proof of title. A "
            "wrong entry therefore does not by itself take away ownership, but it will block a "
            "sale, a crop loan, compensation and most agricultural schemes until corrected. "
            "Clerical errors are corrected by application to the tehsildar. A disputed entry goes "
            "before the revenue court, with appeal to the Sub-Divisional Officer and the Collector; "
            "a question of title itself has to go to a civil court. "
            "Where survey numbers do not match the ground, apply for re-survey or demarcation "
            "through the district survey office."
        ),
        source_url=INDIA_CODE,
        topics=("land records", "bhulekh", "record of rights", "7/12", "khatauni",
                "wrong entry"),
        also_known_as=("jamabandi", "pahani", "rtc", "khasra khatauni", "land map"),
    ),
    Passage(
        id="voter_registration",
        title="Getting on the electoral roll",
        act="Representation of the People Act, 1950",
        section="Sections 19–23; Registration of Electors Rules, 1960",
        text=(
            "Any citizen ordinarily resident in a constituency who is eighteen or over on the "
            "qualifying date may be registered. There are now four qualifying dates a year — the "
            "first of January, April, July and October — so a young voter no longer waits up to a "
            "year to enrol. "
            "Apply on Form 6 through the Voters' Service Portal, the Voter Helpline app or the "
            "Booth Level Officer. Form 8 covers correction of details, transfer to another "
            "constituency and a replacement card; objections to an entry use Form 7. "
            "A voter may be registered in only one constituency, and holding the card is not the "
            "same as being on the roll — always verify the entry before an election, because "
            "deletion during revision is the commonest reason people are turned away. "
            "Anyone on the roll may vote on producing an alternative photo identity document if the "
            "card is unavailable. Refusal or wrongful deletion is appealable to the District "
            "Election Officer and then the Chief Electoral Officer; complaints go to 1950."
        ),
        source_url="https://voters.eci.gov.in",
        topics=("voter id", "electoral roll", "form 6", "epic", "registration"),
        also_known_as=("voter card", "epic card", "name not on voter list"),
    ),
    Passage(
        id="cpgrams_grievance",
        title="Complaining about a government department",
        act="Department of Administrative Reforms and Public Grievances; "
            "State Public Services Guarantee Acts",
        section="CPGRAMS guidelines; State RTS Acts",
        text=(
            "CPGRAMS is the central grievance portal covering ministries, departments and most "
            "central public bodies. Lodge a complaint at pgportal.gov.in, track it by the "
            "registration number, and escalate through the appeal facility if the reply is "
            "unsatisfactory. Target disposal is within twenty-one days for most categories. "
            "It is for administrative grievances, not for matters that are sub judice, and not a "
            "substitute for RTI where what you want is information rather than redress. "
            "More than half the States have a Right to Service or Public Services Guarantee Act, "
            "which is stronger where it applies: it notifies specific services — a caste "
            "certificate, a ration card, a water connection — with a statutory time limit, names a "
            "designated officer, and provides an appeal and a penalty on that officer for "
            "unjustified delay. Where such an Act covers your service, cite it by name and section "
            "in the application, because it converts a request into an enforceable entitlement. "
            "Persistent inaction is also amenable to a writ petition for mandamus."
        ),
        source_url="https://pgportal.gov.in",
        topics=("cpgrams", "government complaint", "right to service", "grievance",
                "public services guarantee"),
        also_known_as=("pgportal", "rts act", "sarkari complaint", "mandamus"),
    ),

    # ── Digital life ────────────────────────────────────────────────────
    Passage(
        id="social_media_grievance",
        title="Getting content about you taken down",
        act="Information Technology (Intermediary Guidelines and Digital Media Ethics Code) "
            "Rules, 2021",
        section="Rules 3(1)(b), 3(2) and 4(8); Grievance Appellate Committee",
        text=(
            "Every significant intermediary must publish the name and contact of a Grievance "
            "Officer, acknowledge a complaint within twenty-four hours and dispose of it within "
            "fifteen days. "
            "For the most serious categories the clock is much shorter: content that exposes a "
            "person's private area, shows nudity or a sexual act, or is impersonation including "
            "morphed images, must be removed within twenty-four hours of a complaint by the "
            "individual or someone on their behalf. "
            "If the platform does not act, appeal to a Grievance Appellate Committee within thirty "
            "days, online and free of charge; it must decide within thirty days. "
            "Unlawful content can also be ordered blocked by the government under Section 69A of "
            "the IT Act, and a court can order takedown. Non-consensual intimate images are "
            "separately an offence, and can be reported anonymously on the National Cyber Crime "
            "Reporting Portal, which has a dedicated route for women and children."
        ),
        source_url="https://www.meity.gov.in",
        topics=("takedown", "social media", "grievance officer", "gac", "content removal"),
        also_known_as=("it rules 2021", "report a post", "deepfake removal"),
    ),
    Passage(
        id="online_impersonation",
        title="Fake profiles, morphed images and deepfakes",
        act="Information Technology Act, 2000 and Bharatiya Nyaya Sanhita, 2023",
        section="Sections 66C, 66D, 66E and 67 of the IT Act; Sections 319 and 356, BNS",
        text=(
            "Using someone's electronic signature, password or other unique identification feature "
            "dishonestly is identity theft under Section 66C, punishable with up to three years and "
            "a fine. Cheating by personation using a computer resource is Section 66D, also up to "
            "three years. Capturing or publishing an image of a private area without consent is "
            "Section 66E. "
            "A morphed or synthetic image used to defame carries Section 356 BNS for defamation, "
            "and where the content is obscene or sexually explicit, Sections 67 and 67A of the IT "
            "Act apply, with heavier punishment where a child is depicted. "
            "Preserve evidence before reporting: full-page screenshots showing the URL and the "
            "date, the profile link, and any messages. Do not delete your own account. "
            "Report on cybercrime.gov.in or 1930, and simultaneously to the platform's Grievance "
            "Officer, which triggers the twenty-four hour removal obligation for impersonation."
        ),
        source_url=INDIA_CODE,
        topics=("fake profile", "deepfake", "identity theft", "morphed photo", "impersonation"),
        also_known_as=("66c", "66d", "fake account", "ai generated image"),
    ),
]
