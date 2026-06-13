"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Shield, Search, Loader2 } from "lucide-react";

interface Message {
  id: number;
  content: string;
  sender_id: number;
  receiver_id: number;
  case_id: number | null;
  created_at: string;
}

interface Case {
  id: number;
  title: string;
  description: string;
  status: string;
  client_id: number;
  lawyer_id: number | null;
  created_at: string;
}

export default function MessagesPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<{ id: number; role: string } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setCurrentUser({ id: parseInt(payload.sub), role: payload.role });
    } catch (e) {
      router.push("/login");
      return;
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token || !currentUser) return;

    fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/cases", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then((data: Case[]) => {
        setCases(data);
        if (data.length > 0) {
          setSelectedCase(data[0]);
        }
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, [currentUser]);

  const fetchMessages = () => {
    if (!selectedCase || !currentUser) return;
    
    const token = localStorage.getItem("token");
    const targetUserId = currentUser.role === "client" ? selectedCase.lawyer_id : selectedCase.client_id;
    
    if (!targetUserId) return; // Cannot fetch messages if no target user

    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/chat/${targetUserId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setMessages(data);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000); // Poll for new messages
    return () => clearInterval(interval);
  }, [selectedCase, currentUser]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedCase || !currentUser) return;

    const token = localStorage.getItem("token");
    const targetUserId = currentUser.role === "client" ? selectedCase.lawyer_id : selectedCase.client_id;
    
    if (!targetUserId) return;

    fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api/chat", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ 
        receiver_id: targetUserId, 
        content: newMessage,
        case_id: selectedCase.id
      })
    }).then(res => {
      if (res.ok) {
        setNewMessage("");
        fetchMessages();
      }
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-73px)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-black" />
      </div>
    );
  }

  const targetUserId = selectedCase 
    ? (currentUser?.role === "client" ? selectedCase.lawyer_id : selectedCase.client_id)
    : null;

  return (
    <div className="min-h-[calc(100vh-73px)] bg-gray-50/50 p-4 lg:p-8 animate-fade-in-up">
      <div className="max-w-6xl mx-auto bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden flex h-[80vh]">
        
        {/* Sidebar */}
        <div className="w-1/3 border-r border-gray-100 flex-col hidden md:flex">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Messages</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input 
                type="text" 
                placeholder="Search cases..." 
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-gray-50 border-transparent focus:bg-white focus:border-gray-200 focus:ring-2 focus:ring-black outline-none transition-all text-sm"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {cases.length === 0 ? (
              <div className="p-6 text-center text-sm text-gray-500">
                No cases found.
              </div>
            ) : (
              cases.map(c => (
                <div 
                  key={c.id}
                  onClick={() => setSelectedCase(c)}
                  className={`p-4 cursor-pointer border-l-2 transition-colors ${selectedCase?.id === c.id ? 'bg-gray-50/80 border-slate-900' : 'border-transparent hover:bg-gray-50'}`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-700">
                      {c.title.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-baseline mb-1">
                        <h3 className="font-semibold text-gray-900 truncate">{c.title}</h3>
                        <span className="text-xs text-gray-400 capitalize">{c.status}</span>
                      </div>
                      <p className="text-sm text-gray-500 truncate">
                        {currentUser?.role === 'client' 
                          ? (c.lawyer_id ? 'Assigned to Lawyer' : 'Unassigned') 
                          : 'Client Chat'}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-gray-50/30">
          {!selectedCase ? (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400 space-y-3">
              <Shield className="w-12 h-12 opacity-20" />
              <p className="text-sm">Select a case to view messages.</p>
            </div>
          ) : (
            <>
              {/* Chat Header */}
              <div className="px-6 py-5 border-b border-gray-100 bg-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700">
                    {selectedCase.title.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{selectedCase.title}</h3>
                    <div className="flex items-center gap-1.5 text-xs font-medium text-gray-500">
                      Case #{selectedCase.id} • {selectedCase.status}
                    </div>
                  </div>
                </div>
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-full text-xs font-medium border border-green-100">
                  <Shield className="w-3.5 h-3.5" /> End-to-end Encrypted
                </div>
              </div>

              {/* Messages List */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {!targetUserId ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-3">
                    <Shield className="w-12 h-12 opacity-20" />
                    <p className="text-sm">This case has not been assigned a lawyer yet.</p>
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-3">
                    <Shield className="w-12 h-12 opacity-20" />
                    <p className="text-sm">This conversation is secure. Say hello!</p>
                  </div>
                ) : (
                  messages.map(msg => {
                    const isMine = msg.sender_id === currentUser?.id;
                    return (
                      <div key={msg.id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[75%] px-5 py-3 rounded-2xl ${isMine ? 'bg-black text-white rounded-br-sm' : 'bg-white border border-gray-100 shadow-sm text-gray-900 rounded-bl-sm'}`}>
                          <p className="text-sm leading-relaxed">{msg.content}</p>
                          <span className={`text-[10px] block mt-1.5 opacity-60 ${isMine ? 'text-right' : 'text-left'}`}>
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 bg-white border-t border-gray-100">
                <form onSubmit={handleSend} className="flex items-center gap-3 relative">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={e => setNewMessage(e.target.value)}
                    placeholder={targetUserId ? "Type a secure message..." : "Waiting for assignment..."}
                    disabled={!targetUserId}
                    className="flex-1 bg-gray-50 border border-transparent focus:border-gray-200 focus:bg-white rounded-full pl-6 pr-14 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-black transition-all disabled:opacity-50"
                  />
                  <button 
                    type="submit"
                    disabled={!newMessage.trim() || !targetUserId}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-black text-white rounded-full hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-4 h-4 -ml-0.5" />
                  </button>
                </form>
              </div>
            </>
          )}
        </div>

      </div>
    </div>
  );
}
