"use client";

import { useEffect, useState } from "react";
import { Scale, Search, Star, MessageSquare } from "lucide-react";

interface Lawyer {
  id: number;
  name: string;
  specialties: string | null;
  experience_years: number | null;
}

export default function LawyersPage() {
  const [lawyers, setLawyers] = useState<Lawyer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/lawyers")
      .then(res => res.json())
      .then(data => {
        setLawyers(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-[calc(100vh-73px)] bg-gray-50/50 py-12 px-6 animate-fade-in-up font-sans">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6 bg-white p-8 rounded-[2rem] border border-gray-200 shadow-sm">
          <div>
            <h1 className="text-4xl font-serif font-bold tracking-tight text-slate-900 mb-2">Find a Lawyer</h1>
            <p className="text-gray-500">Connect with top legal professionals specialized in your needs.</p>
          </div>
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search by name or specialty..." 
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all"
            />
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm animate-pulse">
                <div className="w-16 h-16 bg-gray-200 rounded-full mb-4" />
                <div className="h-5 bg-gray-200 rounded-md w-3/4 mb-2" />
                <div className="h-4 bg-gray-200 rounded-md w-1/2 mb-6" />
                <div className="h-10 bg-gray-200 rounded-xl w-full" />
              </div>
            ))}
          </div>
        ) : lawyers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lawyers.map(lawyer => (
              <div key={lawyer.id} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow group">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center text-xl font-bold text-gray-600">
                    {lawyer.name.charAt(0)}
                  </div>
                  <div className="flex items-center gap-1 bg-yellow-50 text-yellow-700 px-2 py-1 rounded-md text-xs font-medium">
                    <Star className="w-3 h-3 fill-current" /> 4.9
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">{lawyer.name}</h3>
                <div className="text-sm text-gray-500 mb-4 h-10">
                  {lawyer.specialties || "General Practice"} • {lawyer.experience_years || 5} years exp.
                </div>
                <button className="w-full flex items-center justify-center gap-2 bg-gray-50 hover:bg-black hover:text-white text-gray-900 font-medium py-2.5 rounded-xl transition-colors">
                  <MessageSquare className="w-4 h-4" /> Message
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-3xl border border-gray-100 shadow-sm">
            <Scale className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No lawyers found</h3>
            <p className="text-gray-500 max-w-sm mx-auto">There are no registered lawyers in the system yet. Be the first to join!</p>
          </div>
        )}
      </div>
    </div>
  );
}
