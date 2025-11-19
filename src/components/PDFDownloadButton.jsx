import React from "react";

export default function PDFDownloadButton({url}){
  return (
    <div>
      <a href={url || "#"} target="_blank" rel="noreferrer" className={`px-4 py-2 rounded ${url ? "bg-accent text-white" : "bg-slate-700 text-slate-400 cursor-not-allowed"}`}>
        Download Annotated PDF
      </a>
    </div>
  );
}
