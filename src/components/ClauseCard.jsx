import { useState } from "react";
import RiskBadge from "./RiskBadge";

export default function ClauseCard({ clause, onClick }) {
  const [expanded, setExpanded] = useState(false);
  const maxLength = 200;
  const needsTruncation = clause.text && clause.text.length > maxLength;
  const displayText = expanded || !needsTruncation 
    ? clause.text 
    : clause.text.substring(0, maxLength) + "...";

  return (
    <div
      className="glass-card hover:scale-[1.01] transition"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <h3 className="text-lg font-semibold text-white">{clause.type}</h3>
            <RiskBadge risk={clause.risk_level || clause.risk} />
          </div>
          
          <p className="text-gray-300 mt-2 leading-relaxed">{displayText}</p>
          
          {needsTruncation && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="mt-2 text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              {expanded ? "Show Less" : "Show More"}
            </button>
          )}
          
          {clause.explanation && (
            <div className="mt-3 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
              <p className="text-sm text-gray-400">
                <span className="font-semibold text-amber-400">Risk: </span>
                {clause.explanation}
              </p>
            </div>
          )}
        </div>
      </div>
      
      <button
        onClick={onClick}
        className="mt-3 w-full py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-colors"
      >
        View Details & Recommendations
      </button>
    </div>
  );
}
