"use client";

import { useEffect, useState } from "react";
import { Briefcase, Clock, Plus, Shield } from "lucide-react";

interface Case {
  id: number;
  title: string;
  description: string;
  status: string;
  client_id: number;
  created_at: string;
}

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [userRole, setUserRole] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUserRole(payload.role);
        setUserId(parseInt(payload.sub));
      } catch (e) {
        console.error("Invalid token");
      }
    }
    fetchCases();
  }, []);

  const fetchCases = () => {
    const token = localStorage.getItem("token");
    fetch("http://localhost:8000/api/cases", {
      headers: token ? { "Authorization": `Bearer ${token}` } : {}
    })
      .then(res => res.json())
      .then(data => {
        setCases(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const handlePostCase = (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    fetch("http://localhost:8000/api/cases", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ title: newTitle, description: newDescription, client_id: userId || 1 }) 
    }).then(() => {
      setIsModalOpen(false);
      setNewTitle("");
      setNewDescription("");
      fetchCases();
    });
  };

  return (
    <div className="min-h-[calc(100vh-73px)] bg-gray-50/50 py-12 px-6 animate-fade-in-up font-sans">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6 bg-white p-8 rounded-[2rem] border border-gray-200 shadow-sm">
          <div>
            <h1 className="text-4xl font-serif font-bold tracking-tight text-slate-900 mb-2">Case Board</h1>
            <p className="text-gray-500">Clients post their legal issues here for top lawyers to review.</p>
          </div>
          {userRole !== 'lawyer' && (
            <button 
              onClick={() => setIsModalOpen(true)}
              className="flex items-center justify-center gap-2 bg-slate-900 text-white px-6 py-3 rounded-full text-sm font-medium hover:bg-slate-800 transition-colors shrink-0 shadow-md"
            >
              <Plus className="w-4 h-4" /> Post a Case
            </button>
          )}
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm animate-pulse h-32" />
            ))}
          </div>
        ) : cases.length > 0 ? (
          <div className="space-y-4">
            {cases.map(c => (
              <div key={c.id} className="bg-white rounded-2xl p-6 md:p-8 border border-gray-100 shadow-sm hover:shadow-md transition-all group">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-xl font-semibold text-gray-900 group-hover:text-black">{c.title}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider ${c.status === 'open' ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600'}`}>
                    {c.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-6 leading-relaxed line-clamp-2">{c.description}</p>
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1.5"><Clock className="w-4 h-4" /> Posted {new Date(c.created_at).toLocaleDateString()}</div>
                  <div className="flex items-center gap-1.5"><Shield className="w-4 h-4" /> Verified Client #{c.client_id}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-3xl border border-gray-100 shadow-sm">
            <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No cases available</h3>
            <p className="text-gray-500">There are no open cases right now. Check back later.</p>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in-overlay">
          <div className="bg-white rounded-3xl p-8 max-w-lg w-full shadow-2xl animate-fade-in-up border border-gray-100">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">Post a Case</h2>
            <form onSubmit={handlePostCase}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Case Title</label>
                <input 
                  type="text" 
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-black"
                  placeholder="e.g. Need help reviewing a startup employment contract"
                />
              </div>
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea 
                  required
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-black h-32 resize-none"
                  placeholder="Describe your legal issue..."
                />
              </div>
              <div className="flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-5 py-2.5 rounded-full text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="bg-black text-white px-6 py-2.5 rounded-full text-sm font-medium hover:bg-gray-800 transition-colors"
                >
                  Post Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
