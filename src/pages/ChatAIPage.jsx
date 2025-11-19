import React, { useState } from "react";
import { askAI } from "../utils/api";

export default function ChatAIPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const send = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((m) => [...m, userMsg]);

    const response = await askAI(input);
    const botMsg = { sender: "ai", text: response.reply };

    setMessages((m) => [...m, botMsg]);

    setInput("");
  };

  return (
    <div className="glass-card h-[75vh] flex flex-col">
      <h1 className="text-2xl text-white font-bold mb-4">AI Assistant</h1>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-xl max-w-[80%] ${
              m.sender === "user"
                ? "bg-[rgba(76,201,240,0.3)] text-white ml-auto"
                : "bg-[rgba(114,9,183,0.3)] text-white mr-auto"
            }`}
          >
            {m.text}
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <input
          className="flex-1 bg-[rgba(255,255,255,0.1)] border border-[rgba(255,255,255,0.2)]
            rounded-xl px-4 py-2 text-white"
          placeholder="Ask anything about the clause..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="neon-btn" onClick={send}>
          Send
        </button>
      </div>
    </div>
  );
}
