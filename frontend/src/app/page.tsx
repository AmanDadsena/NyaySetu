"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Star,
  ChevronDown,
  FileText,
  Scale,
  MessageSquare,
  Shield,
  CheckCircle2,
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("analyze");

  // Tab auto-cycle
  useEffect(() => {
    const tabs = ["analyze", "lawyers", "cases", "storage"];
    const interval = setInterval(() => {
      setActiveTab((current) => {
        const currentIndex = tabs.indexOf(current);
        return tabs[(currentIndex + 1) % tabs.length];
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-white font-sans text-black overflow-hidden">

      {/* HERO SECTION */}
      <main className="px-6 pt-24 pb-32 max-w-7xl mx-auto text-center">
        {/* Reviews Badge */}
        <div
          className="inline-flex items-center gap-2 mb-8 animate-fade-in-up"
          style={{ animationDelay: "0.2s", opacity: 0 }}
        >
          <div className="w-6 h-6 border border-gray-300 rounded flex items-center justify-center bg-gray-50">
            <Scale className="w-3.5 h-3.5 text-black" />
          </div>
          <span className="text-sm font-medium text-black">
            Open Source AI Legal Assistant for India
          </span>
        </div>

        {/* Main Heading */}
        <h1
          className="text-6xl md:text-7xl lg:text-[80px] font-normal leading-[1.1] tracking-tight mb-5 animate-fade-in-up"
          style={{ animationDelay: "0.3s", opacity: 0 }}
        >
          Resolve Smarter. Move Faster.
          <br />
          <span className="bg-gradient-to-r from-black via-gray-500 to-gray-400 bg-clip-text text-transparent font-semibold">
            AI Powers Your Legal Workflow.
          </span>
        </h1>

        {/* Subheading */}
        <p
          className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto animate-fade-in-up"
          style={{ animationDelay: "0.4s", opacity: 0 }}
        >
          Intelligent automation syncs with your practice to streamline case
          analysis, connect with clients, and save time.
        </p>

        {/* CTA Button */}
        <div
          className="animate-fade-in-up"
          style={{ animationDelay: "0.5s", opacity: 0 }}
        >
          <Link
            href="/analyze"
            className="inline-block bg-black text-white px-8 py-3 rounded-full text-base font-medium hover:bg-gray-800 transition-colors mb-12 shadow-lg shadow-black/10"
          >
            Start Analyzing Documents
          </Link>
        </div>

        {/* Tab Bar */}
        <div
          className="animate-fade-in-up max-w-3xl mx-auto mb-12"
          style={{ animationDelay: "0.6s", opacity: 0 }}
        >
          <div className="bg-gray-100/80 backdrop-blur-sm rounded-xl p-1.5 border border-gray-200/50 shadow-sm">
            {/* Mobile: 2x2 grid */}
            <div className="grid grid-cols-2 gap-1 md:hidden">
              <TabButton
                id="analyze"
                icon={<FileText className="w-4 h-4" />}
                label="Analyze"
                active={activeTab === "analyze"}
                onClick={() => setActiveTab("analyze")}
              />
              <TabButton
                id="lawyers"
                icon={<Scale className="w-4 h-4" />}
                label="Find Lawyer"
                active={activeTab === "lawyers"}
                onClick={() => setActiveTab("lawyers")}
              />
              <TabButton
                id="cases"
                icon={<MessageSquare className="w-4 h-4" />}
                label="Discuss"
                active={activeTab === "cases"}
                onClick={() => setActiveTab("cases")}
              />
              <TabButton
                id="storage"
                icon={<Shield className="w-4 h-4" />}
                label="Secure"
                active={activeTab === "storage"}
                onClick={() => setActiveTab("storage")}
              />
            </div>

            {/* Desktop: Row with dividers */}
            <div className="hidden md:flex items-center justify-between">
              <TabButton
                id="analyze"
                icon={<FileText className="w-4 h-4" />}
                label="Analyze Documents"
                active={activeTab === "analyze"}
                onClick={() => setActiveTab("analyze")}
              />
              <div className="w-px h-5 bg-gray-300 mx-1" />
              <TabButton
                id="lawyers"
                icon={<Scale className="w-4 h-4" />}
                label="Find Lawyers"
                active={activeTab === "lawyers"}
                onClick={() => setActiveTab("lawyers")}
              />
              <div className="w-px h-5 bg-gray-300 mx-1" />
              <TabButton
                id="cases"
                icon={<MessageSquare className="w-4 h-4" />}
                label="Case Discussions"
                active={activeTab === "cases"}
                onClick={() => setActiveTab("cases")}
              />
              <div className="w-px h-5 bg-gray-300 mx-1" />
              <TabButton
                id="storage"
                icon={<Shield className="w-4 h-4" />}
                label="Secure Storage"
                active={activeTab === "storage"}
                onClick={() => setActiveTab("storage")}
              />
            </div>
          </div>
        </div>

        {/* Video + Overlay Section */}
        <div
          className="relative rounded-[2rem] overflow-hidden h-[400px] md:h-[500px] max-w-5xl mx-auto shadow-2xl ring-1 ring-gray-200 animate-fade-in-up bg-gray-50"
          style={{ animationDelay: "0.7s", opacity: 0 }}
        >
          <video
            src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260319_165750_358b1e72-c921-48b7-aaac-f200994f32fb.mp4"
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 w-full h-full object-cover"
          />

          {/* Conditional Overlays */}
          {activeTab === "analyze" && (
            <div className="absolute inset-0 bg-black/20 animate-fade-in-overlay backdrop-blur-[2px]">
              <div className="absolute top-1/2 left-1/2 animate-slide-up-overlay w-[90%] max-w-sm bg-white/95 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/20 text-left">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Document Analysis
                    </h3>
                    <p className="text-xs text-gray-500">Extracting clauses...</p>
                  </div>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
                  <div className="h-full bg-purple-500 w-1/4 rounded-full" />
                </div>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-500" />
                    Scanning document structure
                  </li>
                  <li className="flex items-center gap-2 opacity-50">
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                    Identifying risk flags
                  </li>
                  <li className="flex items-center gap-2 opacity-50">
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                    Extracting key entities
                  </li>
                  <li className="flex items-center gap-2 opacity-50">
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                    Generating summary
                  </li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === "lawyers" && (
            <div className="absolute inset-0 bg-black/20 animate-fade-in-overlay backdrop-blur-[2px]">
              <div className="absolute top-1/2 left-1/2 animate-slide-up-overlay w-[90%] max-w-sm bg-white/95 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/20 text-left">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                    <Scale className="w-5 h-5 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Find an Expert
                    </h3>
                    <p className="text-xs text-gray-500">
                      Matching your legal issue
                    </p>
                  </div>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
                  <div className="h-full bg-orange-500 w-[67%] rounded-full" />
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                    <div className="text-gray-500 text-xs mb-1">Available</div>
                    <div className="font-semibold text-gray-900">142 Lawyers</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                    <div className="text-gray-500 text-xs mb-1">Match Rate</div>
                    <div className="font-semibold text-gray-900">94%</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                    <div className="text-gray-500 text-xs mb-1">Response Time</div>
                    <div className="font-semibold text-gray-900">&lt; 1 hour</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                    <div className="text-gray-500 text-xs mb-1">Specialties</div>
                    <div className="font-semibold text-gray-900">12+</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "cases" && (
            <div className="absolute inset-0 bg-black/20 animate-fade-in-overlay backdrop-blur-[2px]">
              <div className="absolute top-1/2 left-1/2 animate-slide-up-overlay w-[90%] max-w-sm bg-white/95 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/20 text-left">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Case Discussions
                    </h3>
                    <p className="text-xs text-gray-500">Secure messaging</p>
                  </div>
                </div>
                <div className="bg-green-50 text-green-800 text-sm font-medium px-4 py-3 rounded-xl border border-green-200 flex items-center justify-between mb-4">
                  <span>End-to-end Encrypted</span>
                  <Shield className="w-4 h-4" />
                </div>
                <div className="space-y-3">
                  <div className="bg-gray-100 w-3/4 h-10 rounded-tl-xl rounded-tr-xl rounded-br-xl p-3 flex items-center">
                    <div className="h-2 w-20 bg-gray-300 rounded-full" />
                  </div>
                  <div className="bg-blue-600 text-white w-3/4 h-10 rounded-tl-xl rounded-tr-xl rounded-bl-xl p-3 flex items-center ml-auto justify-end">
                    <div className="h-2 w-24 bg-blue-400 rounded-full" />
                  </div>
                  <div className="bg-gray-100 w-1/2 h-10 rounded-tl-xl rounded-tr-xl rounded-br-xl p-3 flex items-center">
                    <div className="h-2 w-16 bg-gray-300 rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "storage" && (
            <div className="absolute inset-0 bg-black/20 animate-fade-in-overlay backdrop-blur-[2px]">
              <div className="absolute top-1/2 left-1/2 animate-slide-up-overlay w-[90%] max-w-sm bg-white/95 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/20 text-left">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Secure Vault
                    </h3>
                    <p className="text-xs text-gray-500">
                      Bank-level encryption
                    </p>
                  </div>
                </div>
                <ul className="space-y-3 text-sm text-gray-700 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-500" />
                    SOC2 Compliant Storage
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-500" />
                    Role-based Access Control
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-500" />
                    Automated Backups
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-500" />
                    Tamper-proof Audit Logs
                  </li>
                </ul>
                <button className="w-full bg-blue-600 text-white font-medium py-2.5 rounded-xl hover:bg-blue-700 transition-colors">
                  Upload Documents
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Knowledge Base Section */}
        <div
          className="mt-24 max-w-4xl mx-auto animate-fade-in-up"
          style={{ animationDelay: "0.8s", opacity: 0 }}
        >
          <p className="text-sm text-gray-500 mb-8 font-medium tracking-wide uppercase">
            Comprehensive Legal Knowledge Base
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 md:gap-8 text-gray-700">
            <a href="https://legislative.gov.in/constitution-of-india" target="_blank" rel="noopener noreferrer" className="bg-gray-50 border border-gray-200 px-6 py-3 rounded-full font-semibold text-sm tracking-wide flex items-center gap-2 shadow-sm hover:shadow-md hover:bg-white hover:border-purple-300 transition-all cursor-pointer group">
              <Scale className="w-4 h-4 text-purple-500 group-hover:scale-110 transition-transform" /> The Constitution of India
            </a>
            <a href="https://main.sci.gov.in/judgments" target="_blank" rel="noopener noreferrer" className="bg-gray-50 border border-gray-200 px-6 py-3 rounded-full font-semibold text-sm tracking-wide flex items-center gap-2 shadow-sm hover:shadow-md hover:bg-white hover:border-blue-300 transition-all cursor-pointer group">
              <FileText className="w-4 h-4 text-blue-500 group-hover:scale-110 transition-transform" /> Supreme Court Judgments
            </a>
            <a href="https://www.indiacode.nic.in" target="_blank" rel="noopener noreferrer" className="bg-gray-50 border border-gray-200 px-6 py-3 rounded-full font-semibold text-sm tracking-wide flex items-center gap-2 shadow-sm hover:shadow-md hover:bg-white hover:border-green-300 transition-all cursor-pointer group">
              <Shield className="w-4 h-4 text-green-500 group-hover:scale-110 transition-transform" /> Statutory Frameworks
            </a>
            <a href="https://www.indiacode.nic.in/handle/123456789/1362" target="_blank" rel="noopener noreferrer" className="bg-gray-50 border border-gray-200 px-6 py-3 rounded-full font-semibold text-sm tracking-wide flex items-center gap-2 shadow-sm hover:shadow-md hover:bg-white hover:border-orange-300 transition-all cursor-pointer group">
              <FileText className="w-4 h-4 text-orange-500 group-hover:scale-110 transition-transform" /> Central & State Acts
            </a>
          </div>
        </div>

        {/* Authentic Stats Section */}
        <div
          className="mt-32 max-w-6xl mx-auto animate-fade-in-up flex flex-col lg:flex-row items-center gap-12 text-left"
          style={{ animationDelay: "0.9s", opacity: 0 }}
        >
          <div className="flex-1 space-y-6">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900">
              Empowering India's Vast Legal Ecosystem
            </h2>
            <p className="text-lg text-gray-600 leading-relaxed">
              Nyaysetu is built to support the monumental scale of the Indian judicial system. 
              Our AI seamlessly connects users with the complex network of courts and legal professionals 
              working tirelessly across the country.
            </p>
            <div className="grid grid-cols-2 gap-6 pt-4">
              <div className="border-l-4 border-black pl-4">
                <div className="text-3xl font-black text-black">20.13L+</div>
                <div className="text-sm font-medium text-gray-500 mt-1 uppercase tracking-wide">Registered Advocates</div>
              </div>
              <div className="border-l-4 border-black pl-4">
                <div className="text-3xl font-black text-black">25</div>
                <div className="text-sm font-medium text-gray-500 mt-1 uppercase tracking-wide">High Courts</div>
              </div>
              <div className="border-l-4 border-black pl-4">
                <div className="text-3xl font-black text-black">22,300+</div>
                <div className="text-sm font-medium text-gray-500 mt-1 uppercase tracking-wide">Subordinate Courts</div>
              </div>
              <div className="border-l-4 border-black pl-4">
                <div className="text-3xl font-black text-black">25,741</div>
                <div className="text-sm font-medium text-gray-500 mt-1 uppercase tracking-wide">District Judicial Officers</div>
              </div>
            </div>
          </div>
          <div className="flex-1 w-full relative rounded-[2rem] overflow-hidden shadow-2xl aspect-[4/3] group border border-gray-100">
            <img 
              src="/supreme_court.png" 
              alt="Supreme Court of India" 
              className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex items-end">
              <div className="p-8 text-white w-full">
                <div className="flex items-center gap-2 mb-2">
                  <Scale className="w-5 h-5 text-amber-400" />
                  <p className="font-semibold text-xl drop-shadow-md">Supreme Court of India</p>
                </div>
                <p className="text-sm text-white/90 drop-shadow-md">The Apex Judicial Authority — 38 Sanctioned Judges</p>
              </div>
            </div>
          </div>
        </div>

        {/* Did You Know Section */}
        <DidYouKnowSection />
      </main>
    </div>
  );
}

// Data and Component for Did You Know
const lawFacts = [
  "The original Constitution of India was not printed; it was meticulously handwritten in both English and Hindi, and decorated by artists from Shantiniketan.",
  "At over 146,000 words, the Constitution of India is the longest written national constitution in the world.",
  "Justice M. Fathima Beevi became the first female judge of the Supreme Court of India in 1989.",
  "The new Bharatiya Nyaya Sanhita (BNS) 2023 replaces the colonial-era Indian Penal Code of 1860, streamlining the sections from 511 to 358.",
  "Under Indian traffic laws, the Motor Vehicles (Amendment) Act of 2019 introduced significant hikes in penalties to deter traffic rule violations like driving without a license or insurance.",
  "Community service has been introduced as a new form of legal punishment under the BNS 2023 for certain minor offences.",
  "The Constituent Assembly took exactly 2 years, 11 months, and 17 days to draft the Constitution of India."
];

function DidYouKnowSection() {
  const [factIndex, setFactIndex] = useState(0);

  useEffect(() => {
    // Pick a random fact on mount
    setFactIndex(Math.floor(Math.random() * lawFacts.length));
    
    // Rotate every 10 seconds
    const interval = setInterval(() => {
      setFactIndex((prev) => (prev + 1) % lawFacts.length);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mt-20 max-w-2xl mx-auto text-left bg-gradient-to-br from-amber-50 to-orange-50/50 p-8 rounded-3xl border border-amber-100 shadow-sm animate-fade-in-up" style={{ animationDelay: "1s", opacity: 0 }}>
      <div className="flex items-center gap-2 mb-3 text-amber-800">
        <Star className="w-5 h-5 fill-amber-500 text-amber-500" />
        <h3 className="font-serif font-bold text-lg">Did You Know?</h3>
      </div>
      <p className="text-gray-700 italic leading-relaxed min-h-[4rem] transition-all duration-500">
        "{lawFacts[factIndex]}"
      </p>
    </div>
  );
}

// Helper component for tab buttons
function TabButton({
  id,
  icon,
  label,
  active,
  onClick,
}: {
  id: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 w-full md:w-auto ${
        active
          ? "bg-white text-black shadow-sm"
          : "text-gray-600 hover:text-black hover:bg-gray-50/50"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
