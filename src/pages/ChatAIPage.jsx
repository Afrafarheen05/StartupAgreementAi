import React, { useState, useEffect, useRef } from "react";
import { askAI } from "../utils/api";
import { Bot, User, Send, Sparkles } from "lucide-react";

export default function ChatAIPage() {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! 👋 I'm your AI legal assistant for startup agreements.\n\nI can help you understand:\n🔴 High-risk clauses (liquidation preference, anti-dilution, board control)\n🟡 Medium-risk terms (vesting, voting rights)\n🟢 Lower-risk clauses (pro-rata rights, information rights)\n\nAsk me anything!"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { sender: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await askAI(input);
      const botMsg = { sender: "ai", text: response.reply };
      setMessages((m) => [...m, botMsg]);
    } catch (error) {
      const errorMsg = { 
        sender: "ai", 
        text: "Sorry, I encountered an error. Please try again or ask a different question." 
      };
      setMessages((m) => [...m, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const quickQuestions = [
    "What is liquidation preference?",
    "Explain anti-dilution protection",
    "What are red flags in my agreement?",
    "How should I negotiate board control?"
  ];

  return (
    <div className="h-[85vh] flex flex-col">
      <div className="glass-card flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-700">
          <div>
            <h1 className="text-2xl text-white font-bold flex items-center gap-2">
              <Bot className="w-7 h-7 text-purple-400" />
              AI Legal Assistant
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Powered by intelligent NLP • Real-time responses
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm font-semibold">Online</span>
          </div>
        </div>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="mb-4">
            <p className="text-gray-400 text-sm mb-2">💡 Quick questions:</p>
            <div className="grid grid-cols-2 gap-2">
              {quickQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => setInput(q)}
                  className="text-left px-3 py-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 hover:border-purple-500/50 text-gray-300 text-sm transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 custom-scrollbar">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-3 ${m.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
            >
              {/* Avatar */}
              <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                m.sender === "user" 
                  ? "bg-gradient-to-br from-blue-500 to-cyan-600" 
                  : "bg-gradient-to-br from-purple-500 to-pink-600"
              }`}>
                {m.sender === "user" ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Sparkles className="w-5 h-5 text-white" />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[75%] p-4 rounded-2xl ${
                  m.sender === "user"
                    ? "bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 text-white"
                    : "bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 text-gray-200"
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                <span className="text-xs text-gray-500 mt-2 block">
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-purple-500 to-pink-600">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 p-4 rounded-2xl">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex gap-3 pt-4 border-t border-gray-700">
          <textarea
            className="flex-1 bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            placeholder="Ask anything about startup agreements..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={1}
            disabled={loading}
          />
          <button 
            className="neon-btn px-6 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={send}
            disabled={loading || !input.trim()}
          >
            <Send className="w-5 h-5" />
            Send
          </button>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(168, 85, 247, 0.5);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(168, 85, 247, 0.7);
        }
        .delay-100 {
          animation-delay: 0.1s;
        }
        .delay-200 {
          animation-delay: 0.2s;
        }
      `}</style>
    </div>
  );
}
