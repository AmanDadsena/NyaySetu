"use client";

import { useState } from "react";
import { Scale, BookOpen, Shield, Award, Landmark, CheckCircle2, FileText, Globe } from "lucide-react";

export default function KnowledgeBase() {
  const [activeSection, setActiveSection] = useState<"constitution" | "bns" | "landmark" | "cyber">("constitution");

  return (
    <div className="min-h-screen bg-white font-sans text-black overflow-hidden pb-32">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-amber-50 to-white -z-10" />

      <main className="px-6 pt-24 max-w-5xl mx-auto">
        <div className="text-center mb-16 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 bg-amber-100/50 text-amber-800 rounded-full border border-amber-200">
            <Landmark className="w-4 h-4" />
            <span className="text-sm font-medium">Authentic Legal Intelligence</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-serif font-bold text-slate-900 mb-6 tracking-tight">
            Indian Legal <span className="text-amber-600">Knowledge Base</span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Explore authentic insights into the Constitution, Bharatiya Nyaya Sanhita, landmark judgments, and cyber laws of India.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap p-1.5 bg-gray-100 rounded-2xl mb-12 max-w-4xl mx-auto shadow-inner gap-1">
          <button
            onClick={() => setActiveSection("constitution")}
            className={`flex-1 min-w-[150px] flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${
              activeSection === "constitution" ? "bg-white text-slate-900 shadow-md" : "text-gray-500 hover:text-slate-900 hover:bg-gray-50/50"
            }`}
          >
            <Scale className="w-4 h-4" /> Constitution
          </button>
          <button
            onClick={() => setActiveSection("bns")}
            className={`flex-1 min-w-[150px] flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${
              activeSection === "bns" ? "bg-white text-slate-900 shadow-md" : "text-gray-500 hover:text-slate-900 hover:bg-gray-50/50"
            }`}
          >
            <BookOpen className="w-4 h-4" /> BNS 2023
          </button>
          <button
            onClick={() => setActiveSection("landmark")}
            className={`flex-1 min-w-[150px] flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${
              activeSection === "landmark" ? "bg-white text-slate-900 shadow-md" : "text-gray-500 hover:text-slate-900 hover:bg-gray-50/50"
            }`}
          >
            <Award className="w-4 h-4" /> Landmark Judgments
          </button>
          <button
            onClick={() => setActiveSection("cyber")}
            className={`flex-1 min-w-[150px] flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${
              activeSection === "cyber" ? "bg-white text-slate-900 shadow-md" : "text-gray-500 hover:text-slate-900 hover:bg-gray-50/50"
            }`}
          >
            <Globe className="w-4 h-4" /> Cyber Laws
          </button>
        </div>

        {/* Content Section */}
        <div className="animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          
          {/* CONSTITUTION */}
          {activeSection === "constitution" && (
            <div className="space-y-12">
              <div className="bg-slate-900 text-white rounded-[2rem] p-8 md:p-12 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10">
                  <Landmark className="w-64 h-64" />
                </div>
                <div className="relative z-10">
                  <h2 className="text-3xl font-serif font-bold mb-4 text-amber-400">Fundamental Rights</h2>
                  <p className="text-slate-300 text-lg mb-8 max-w-2xl leading-relaxed">
                    Enshrined in Part III (Articles 12–35) of the Constitution, these rights guarantee human dignity and all-round development. They are justiciable and enforceable by the Supreme Court (Article 32).
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700 hover:border-amber-500/50 transition-colors">
                      <div className="flex items-center gap-3 mb-3">
                        <Scale className="text-amber-500 w-5 h-5" />
                        <h3 className="font-semibold text-lg">Right to Equality (Art. 14–18)</h3>
                      </div>
                      <p className="text-slate-400 text-sm">Equality before the law, prohibition of discrimination, and abolition of untouchability.</p>
                    </div>
                    
                    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700 hover:border-amber-500/50 transition-colors">
                      <div className="flex items-center gap-3 mb-3">
                        <Shield className="text-amber-500 w-5 h-5" />
                        <h3 className="font-semibold text-lg">Right to Freedom (Art. 19–22)</h3>
                      </div>
                      <p className="text-slate-400 text-sm">Guarantees freedom of speech, expression, assembly, movement, and profession.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-xl shadow-black/5 flex flex-col items-center text-center">
                  <h3 className="text-2xl font-serif font-bold text-slate-900 mb-4">State Emblem of India</h3>
                  <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                    The National Emblem is an adaptation of the Lion Capital of Ashoka at Sarnath. It features four Asiatic lions standing back to back, symbolizing power, courage, confidence, and pride.
                  </p>
                  <img src="/emblem.svg" alt="State Emblem of India" className="w-32 h-auto object-contain mt-auto" />
                </div>
                <div className="bg-amber-50 p-8 rounded-3xl border border-amber-100 shadow-xl shadow-amber-900/5">
                  <h3 className="text-2xl font-serif font-bold text-amber-900 mb-4">Key Characteristics</h3>
                  <ul className="space-y-4">
                    <li className="flex gap-3">
                      <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0" />
                      <span className="text-sm text-amber-900/80"><strong>Source of Law:</strong> Limits the authority of the State. Any laws inconsistent with Fundamental Rights are void (Article 13).</span>
                    </li>
                    <li className="flex gap-3">
                      <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0" />
                      <span className="text-sm text-amber-900/80"><strong>Applicability:</strong> Universal to all citizens, though subject to reasonable restrictions.</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* BNS */}
          {activeSection === "bns" && (
            <div className="space-y-12 animate-fade-in-up">
              <div className="bg-white p-8 md:p-12 rounded-[2rem] border border-gray-200 shadow-2xl shadow-black/5 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl -z-10" />
                <h2 className="text-3xl font-serif font-bold mb-4 text-slate-900">Bharatiya Nyaya Sanhita (BNS), 2023</h2>
                <p className="text-gray-600 text-lg mb-8 max-w-3xl leading-relaxed">
                  The BNS is the new penal code of India, enacted on December 25, 2023, replacing the colonial-era Indian Penal Code (IPC), 1860. It establishes a citizen-centric legal structure that is more accessible and affordable.
                </p>

                <div className="grid md:grid-cols-3 gap-6">
                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <div className="text-3xl font-bold text-blue-600 mb-2">358</div>
                    <h3 className="font-semibold text-slate-900 mb-2">Streamlined Sections</h3>
                    <p className="text-sm text-gray-500">Significantly condensed from the IPC's 511 sections, removing irrelevant colonial provisions.</p>
                  </div>
                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <div className="text-3xl font-bold text-blue-600 mb-2">Women & Children</div>
                    <h3 className="font-semibold text-slate-900 mb-2">Prioritized Protection</h3>
                    <p className="text-sm text-gray-500">Crimes against women and children are now prioritized and grouped into a single chapter.</p>
                  </div>
                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <div className="text-3xl font-bold text-blue-600 mb-2">Community</div>
                    <h3 className="font-semibold text-slate-900 mb-2">Service Punishments</h3>
                    <p className="text-sm text-gray-500">Introduces "community service" as a new form of punishment for certain minor offences.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* LANDMARK JUDGMENTS */}
          {activeSection === "landmark" && (
            <div className="space-y-6 animate-fade-in-up">
              <h2 className="text-3xl font-serif font-bold mb-4 text-slate-900">Landmark Supreme Court Judgments</h2>
              
              <div className="bg-white p-8 rounded-[2rem] border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xl font-bold text-slate-900 mb-2">1. Kesavananda Bharati v. State of Kerala (1973)</h3>
                <p className="text-amber-700 text-sm font-semibold mb-3">Basic Structure Doctrine</p>
                <p className="text-gray-600 text-sm leading-relaxed">
                  The most celebrated case in Indian constitutional history. A 13-judge bench established that Parliament can amend any part of the Constitution, but it cannot alter its "Basic Structure" (e.g., secularism, democracy, judicial review). This saved Indian democracy from authoritarian legislative overreach.
                </p>
              </div>

              <div className="bg-white p-8 rounded-[2rem] border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xl font-bold text-slate-900 mb-2">2. Maneka Gandhi v. Union of India (1978)</h3>
                <p className="text-amber-700 text-sm font-semibold mb-3">Expansion of Article 21 (Right to Life)</p>
                <p className="text-gray-600 text-sm leading-relaxed">
                  The Court ruled that the "procedure established by law" for depriving someone of life or personal liberty must be just, fair, and reasonable, not arbitrary. This case radically expanded Article 21 to include a multitude of fundamental rights, such as the right to travel abroad and right to dignity.
                </p>
              </div>

              <div className="bg-white p-8 rounded-[2rem] border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xl font-bold text-slate-900 mb-2">3. Justice K.S. Puttaswamy (Retd.) v. Union of India (2017)</h3>
                <p className="text-amber-700 text-sm font-semibold mb-3">Right to Privacy</p>
                <p className="text-gray-600 text-sm leading-relaxed">
                  A historic 9-judge bench unanimously affirmed that the Right to Privacy is a constitutionally protected fundamental right, intrinsic to the Right to Life and Personal Liberty under Article 21. This severely impacted data protection and state surveillance laws.
                </p>
              </div>
            </div>
          )}

          {/* CYBER LAWS */}
          {activeSection === "cyber" && (
            <div className="space-y-6 animate-fade-in-up">
              <div className="bg-slate-900 p-8 rounded-[2rem] shadow-xl text-white">
                <h2 className="text-3xl font-serif font-bold mb-4 text-emerald-400">Cyber Laws (Information Technology Act, 2000)</h2>
                <p className="text-slate-300 mb-6">
                  The IT Act is the primary law in India dealing with cybercrime and electronic commerce. It penalizes various cybercrimes and provides legal recognition to electronic documents and digital signatures.
                </p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-2">Section 66: Hacking</h3>
                    <p className="text-sm text-slate-400">Fraudulently or dishonestly diminishing the value or utility of computer resources. Punishment: Up to 3 years imprisonment or ₹5 Lakh fine.</p>
                  </div>
                  <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-2">Section 66C: Identity Theft</h3>
                    <p className="text-sm text-slate-400">Fraudulently making use of the electronic signature, password, or any other unique identification feature of any other person.</p>
                  </div>
                  <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-2">Section 43A: Data Protection</h3>
                    <p className="text-sm text-slate-400">Corporate bodies dealing with sensitive personal data must implement reasonable security practices. Failure resulting in wrongful loss can lead to compensation.</p>
                  </div>
                  <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
                    <h3 className="text-lg font-bold text-white mb-2">Section 67: Obscenity</h3>
                    <p className="text-sm text-slate-400">Publishing or transmitting obscene material in electronic form is strictly prohibited and carries severe penalties.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
