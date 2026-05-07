// app/page.tsx
"use client";
import { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { sendChatMessage } from '@/lib/api';

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hello! I am Central Brain for your team. Ask me anything about the project.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = input;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(userMessage);
      setMessages(prev => [
        ...prev,
        {
          role: 'bot',
          content: res.answer,
        },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Chat request failed.';
      setMessages(prev => [...prev, { role: 'bot', content: `Error: ${message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-zinc-900">
      <div className="flex-1 overflow-y-auto space-y-6 p-6 pb-24 max-w-4xl mx-auto w-full">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'bot' && (
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5" />
              </div>
            )}
            <div className={`p-4 rounded-2xl max-w-[80%] ${
              msg.role === 'user' 
              ? 'bg-zinc-100 text-zinc-900 rounded-br-none' 
              : 'bg-zinc-800 border border-white/10 rounded-bl-none text-zinc-200'
            }`}>
              <p className="leading-relaxed">{msg.content}</p>
            </div>
            {msg.role === 'user' && (
              <div className="w-10 h-10 rounded-full bg-zinc-700 flex items-center justify-center shrink-0">
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-zinc-500 animate-pulse flex gap-2 items-center"><Bot className="w-5 h-5"/> Brain is thinking...</div>}
      </div>

      <div className="fixed bottom-0 right-0 left-64 p-6">
        <div className="bg-zinc-800 border border-white/10 p-2 rounded-2xl flex gap-2 shadow-2xl backdrop-blur-xl max-w-4xl mx-auto">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about the project status, code, or docs..." 
            className="flex-1 bg-transparent border-none focus:outline-none px-4 text-zinc-100 placeholder-zinc-500"
          />
          <button 
            onClick={handleSend}
            disabled={loading || !input}
            className="bg-indigo-600 hover:bg-indigo-500 text-white p-3 rounded-xl transition disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}