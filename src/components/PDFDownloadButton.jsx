import React from "react";
import { Download, FileText } from "lucide-react";

export default function PDFDownloadButton({ data }) {
  
  const generatePDF = () => {
    if (!data) {
      alert("No analysis data available");
      return;
    }

    try {
      // Simple approach: Open print dialog which allows save as PDF
      window.print();
    } catch (error) {
      console.error("PDF generation error:", error);
      alert("Failed to generate PDF. Please try again.");
    }
  };

  const downloadJSON = () => {
    if (!data) return;
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis-report-${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-3">
      <button
        onClick={generatePDF}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold transition-colors shadow-lg"
        title="Print report (save as PDF from print dialog)"
      >
        <FileText className="w-4 h-4" />
        Print Report / Save as PDF
      </button>
      
      <button
        onClick={downloadJSON}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-semibold transition-colors shadow-lg"
        title="Download raw analysis data"
      >
        <Download className="w-4 h-4" />
        Download Data
      </button>
    </div>
  );
}
