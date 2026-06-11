import { Scale, Shield, Users, Zap } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white font-sans text-black overflow-hidden py-24">
      {/* Header Section */}
      <div className="max-w-4xl mx-auto px-6 text-center mb-24 animate-fade-in-up">
        <h1 className="text-5xl md:text-6xl font-normal tracking-tight mb-6">
          Bridging the gap between
          <br />
          <span className="bg-gradient-to-r from-black via-gray-500 to-gray-400 bg-clip-text text-transparent font-semibold">
            Law and Technology.
          </span>
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Nyaysetu is built to democratize access to legal understanding and streamline how legal professionals connect with clients.
        </p>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-6 mb-32">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-4 text-center divide-x divide-gray-100 bg-gray-50 rounded-3xl p-8 border border-gray-100 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          <div>
            <div className="text-4xl font-bold mb-2">10k+</div>
            <div className="text-sm text-gray-500 font-medium">Legal Professionals</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">5M+</div>
            <div className="text-sm text-gray-500 font-medium">Clauses Analyzed</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">99%</div>
            <div className="text-sm text-gray-500 font-medium">Accuracy Rate</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">24/7</div>
            <div className="text-sm text-gray-500 font-medium">Availability</div>
          </div>
        </div>
      </div>

      {/* Core Values & Legal Frameworks */}
      <div className="max-w-7xl mx-auto px-6 mb-32">
        <h2 className="text-4xl font-serif font-bold text-center mb-16 text-slate-900">Understanding Indian Laws</h2>
        <div className="grid lg:grid-cols-3 gap-10">
          
          {/* Constitution */}
          <div className="bg-amber-50/50 p-8 rounded-3xl border border-amber-100 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center text-amber-700 mb-6 shadow-sm">
              <Scale className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-serif font-semibold mb-4 text-slate-900">Constitution of India</h3>
            <p className="text-gray-700 leading-relaxed mb-8">
              The supreme law of India, adopted in 1949 and effective since 1950. It guarantees Fundamental Rights to its citizens and outlines the framework defining political principles, procedures, powers, and duties of government institutions.
            </p>
            <a 
              href="https://legislative.gov.in/constitution-of-india" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-slate-800 transition-colors shadow-md"
            >
              Open Official PDF <Zap className="w-4 h-4" />
            </a>
          </div>

          {/* Criminal Laws / BNS */}
          <div className="bg-blue-50/50 p-8 rounded-3xl border border-blue-100 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-blue-700 mb-6 shadow-sm">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-serif font-semibold mb-4 text-slate-900">Bharatiya Nyaya Sanhita (BNS)</h3>
            <p className="text-gray-700 leading-relaxed mb-8">
              The new criminal code of India effective from July 1, 2024, replacing the colonial-era IPC 1860. It prioritizes offences against women and children, streamlines legal sections, and introduces community service as a penal measure.
            </p>
            <a 
              href="https://www.indiacode.nic.in/handle/123456789/21238" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-slate-800 transition-colors shadow-md"
            >
              Open BNS Official Document <Zap className="w-4 h-4" />
            </a>
          </div>

          {/* Traffic Laws */}
          <div className="bg-emerald-50/50 p-8 rounded-3xl border border-emerald-100 animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center text-emerald-700 mb-6 shadow-sm">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-serif font-semibold mb-4 text-slate-900">Traffic & Motor Laws</h3>
            <p className="text-gray-700 leading-relaxed mb-8">
              Governed primarily by the Motor Vehicles Act, 1988 and the strict amendments of 2019. It enforces strict penalties for traffic violations (e.g., driving without a license, overspeeding) using an interconnected E-Challan system across states.
            </p>
            <a 
              href="https://morth.nic.in/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-slate-800 transition-colors shadow-md"
            >
              Visit MoRTH Portal <Zap className="w-4 h-4" />
            </a>
          </div>

        </div>
      </div>

      {/* Official References */}
      <div className="bg-slate-900 text-white py-32 rounded-t-[4rem]">
        <div className="max-w-4xl mx-auto px-6 text-center animate-fade-in-up" style={{ animationDelay: "0.5s" }}>
          <Scale className="w-12 h-12 text-amber-500 mx-auto mb-8" />
          <h2 className="text-3xl md:text-4xl font-serif font-semibold mb-8 text-amber-50">Authentic Government References</h2>
          <p className="text-lg text-slate-300 leading-relaxed mb-12">
            Nyaysetu is committed to providing accurate and authentic legal information. All our legal insights, documents, and reference materials are meticulously sourced from the official portals of the Government of India.
          </p>
          
          <div className="grid sm:grid-cols-2 gap-6 text-left max-w-2xl mx-auto">
            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
              <h4 className="font-semibold text-amber-400 mb-2">Legislative Department</h4>
              <p className="text-sm text-slate-400">Maintains the official text of the Constitution of India and central acts. <br/><a href="https://legislative.gov.in" target="_blank" className="underline hover:text-white mt-2 inline-block">legislative.gov.in</a></p>
            </div>
            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
              <h4 className="font-semibold text-amber-400 mb-2">India Code Portal</h4>
              <p className="text-sm text-slate-400">The digital repository of all Central and State Acts including the BNS 2023. <br/><a href="https://www.indiacode.nic.in" target="_blank" className="underline hover:text-white mt-2 inline-block">indiacode.nic.in</a></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
