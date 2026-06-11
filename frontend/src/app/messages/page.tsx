"use client";

import { useEffect, useState, useRef } from "react";
import { Send, Shield, Search } from "lucide-react";

interface Message {
  id: number;
  content: string;
  sender_id: number;
  created_at: string;
}

export default function MessagesPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Mocked state: Current user is 1, chatting with user 2
  const currentUserId = 1;
  const targetUserId = 2;

  const fetchMessages = () => {
    fetch(`http://localhost:8000/api/chat/${currentUserId}/${targetUserId}`)
      .then(res => res.json())
      .then(data => setMessages(data))
      .catch(() => {});
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000); // Simple poll
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    fetch(`http://localhost:8000/api/chat/${currentUserId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ receiver_id: targetUserId, content: newMessage })
    }).then(() => {
      setNewMessage("");
      fetchMessages();
    });
  };

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
                placeholder="Search conversations..." 
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-gray-50 border-transparent focus:bg-white focus:border-gray-200 focus:ring-2 focus:ring-black outline-none transition-all text-sm"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            <div className="p-4 bg-gray-50/80 cursor-pointer border-l-2 border-slate-900">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-700">A</div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline mb-1">
                    <h3 className="font-semibold text-gray-900 truncate">Advocate Sharma</h3>
                    <span className="text-xs text-gray-400">Now</span>
                  </div>
                  <p className="text-sm text-gray-500 truncate">BNS Section 69 clarification</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-gray-50/30">
          {/* Chat Header */}
          <div className="px-6 py-5 border-b border-gray-100 bg-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700">A</div>
              <div>
                <h3 className="font-semibold text-gray-900">Advocate Sharma</h3>
                <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Online
                </div>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-full text-xs font-medium border border-green-100">
              <Shield className="w-3.5 h-3.5" /> End-to-end Encrypted
            </div>
          </div>

          {/* Messages List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-3">
                <Shield className="w-12 h-12 opacity-20" />
                <p className="text-sm">This conversation is secure. Say hello!</p>
              </div>
            ) : (
              messages.map(msg => {
                const isMine = msg.sender_id === currentUserId;
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
                placeholder="Type a secure message..."
                className="flex-1 bg-gray-50 border border-transparent focus:border-gray-200 focus:bg-white rounded-full pl-6 pr-14 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-black transition-all"
              />
              <button 
                type="submit"
                disabled={!newMessage.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-black text-white rounded-full hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4 -ml-0.5" />
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}
