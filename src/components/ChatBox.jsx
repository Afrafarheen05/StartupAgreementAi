import React, {useState} from "react";

export default function ChatBox({onSend, latestReply}){
  const [text, setText] = useState("");
  const send = async () => {
    if(!text) return;
    await onSend(text);
    setText("");
  };
  return (
    <div className="bg-panel p-4 rounded shadow-card">
      <div className="mb-3 text-sm text-slate-300">AI Assistant</div>
      <div className="flex gap-2">
        <input value={text} onChange={e=>setText(e.target.value)} className="flex-1 bg-transparent border border-white/5 rounded px-3 py-2 text-white" placeholder="Ask about a clause..."/>
        <button onClick={send} className="px-4 py-2 bg-accent rounded text-white">Ask</button>
      </div>
      {latestReply && (
        <div className="mt-4 text-slate-200 bg-[rgba(0,0,0,0.2)] p-3 rounded">
          {latestReply}
        </div>
      )}
    </div>
  );
}
