import React from "react";

export default function Loader(){
  return (
    <div className="flex items-center gap-3 text-slate-300">
      <div className="w-8 h-8 rounded-full border-4 border-t-accent border-slate-600 animate-spin"></div>
      <div>Analyzing — this may take a few seconds...</div>
    </div>
  );
}
