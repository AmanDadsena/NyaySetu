"use client";

import { useState } from "react";
import Link from "next/link";
import { Scale, BookOpen, Shield, Award, Landmark, ChevronDown, CheckCircle2 } from "lucide-react";

export default function KnowledgeBase() {
  const [activeSection, setActiveSection] = useState<"constitution" | "bns">("constitution");

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
            Explore authentic insights into the Constitution of India and the newly enacted Bharatiya Nyaya Sanhita (BNS), 2023.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex p-1.5 bg-gray-100 rounded-2xl mb-12 max-w-md mx-auto shadow-inner">
          <button
            onClick={() => setActiveSection("constitution")}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${
              activeSection === "constitution"
                ? "bg-white text-slate-900 shadow-md"
                : "text-gray-500 hover:text-slate-900 hover:bg-gray-50/50"
            }`}
          >
            <Scale className="w-4 h-4" />
            Constitution of India
          </button>
          <button
            onClick={() => setActiveSection("bns")}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${
              activeSection === "bns"
                ? "bg-white text-slate-900 shadow-md"
                : "text-gray-500 hover:text-slate-900 hover:bg-gray-50/50"
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Bharatiya Nyaya Sanhita
          </button>
        </div>

        {/* Content Section */}
        <div className="animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
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

                    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700 hover:border-amber-500/50 transition-colors">
                      <div className="flex items-center gap-3 mb-3">
                        <Award className="text-amber-500 w-5 h-5" />
                        <h3 className="font-semibold text-lg">Cultural & Educational (Art. 29–30)</h3>
                      </div>
                      <p className="text-slate-400 text-sm">Protects the interests of minorities regarding their language, culture, and institutions.</p>
                    </div>

                    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-700 hover:border-amber-500/50 transition-colors">
                      <div className="flex items-center gap-3 mb-3">
                        <Landmark className="text-amber-500 w-5 h-5" />
                        <h3 className="font-semibold text-lg">Constitutional Remedies (Art. 32)</h3>
                      </div>
                      <p className="text-slate-400 text-sm">Empowers citizens to move the courts. Called the "heart and soul" of the Constitution.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-xl shadow-black/5">
                  <h3 className="text-2xl font-serif font-bold text-slate-900 mb-4">State Emblem of India</h3>
                  <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                    The National Emblem is an adaptation of the Lion Capital of Ashoka at Sarnath. It features four Asiatic lions standing back to back, symbolizing power, courage, confidence, and pride.
                  </p>
                  <img src="/logo.png" alt="Emblem Inspiration" className="w-24 h-24 object-contain opacity-80 mix-blend-multiply" />
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
        </div>
      </main>
    </div>
  );
}
