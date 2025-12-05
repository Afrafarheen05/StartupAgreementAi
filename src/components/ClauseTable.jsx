import React, { useState } from "react";
import ClauseCard from "./ClauseCard";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function ClauseTable({ clauses, onSelect }) {
  const [expandedRisk, setExpandedRisk] = useState({ High: true, Medium: false, Low: false });

  const toggleRiskLevel = (level) => {
    setExpandedRisk(prev => ({ ...prev, [level]: !prev[level] }));
  };

  const highRiskClauses = clauses.filter(c => c.risk === "High");
  const mediumRiskClauses = clauses.filter(c => c.risk === "Medium");
  const lowRiskClauses = clauses.filter(c => c.risk === "Low");

  const RiskSection = ({ level, clauses, color, borderColor, bgColor }) => {
    if (clauses.length === 0) return null;

    return (
      <div className="mb-6">
        <button
          onClick={() => toggleRiskLevel(level)}
          className={`w-full flex items-center justify-between p-4 rounded-lg border-2 ${borderColor} ${bgColor} hover:opacity-90 transition-all`}
        >
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-bold ${color}`}>
              {level}
            </span>
            <span className="text-white font-semibold">
              {clauses.length} {level} Risk Clause{clauses.length !== 1 ? 's' : ''}
            </span>
          </div>
          {expandedRisk[level] ? (
            <ChevronUp className="w-5 h-5 text-white" />
          ) : (
            <ChevronDown className="w-5 h-5 text-white" />
          )}
        </button>

        {expandedRisk[level] && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {clauses.map((c) => (
              <ClauseCard key={c.id} clause={c} onClick={() => onSelect(c)} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <RiskSection
        level="High"
        clauses={highRiskClauses}
        color="bg-red-500 text-white"
        borderColor="border-red-500"
        bgColor="bg-red-500/10"
      />
      <RiskSection
        level="Medium"
        clauses={mediumRiskClauses}
        color="bg-yellow-500 text-black"
        borderColor="border-yellow-500"
        bgColor="bg-yellow-500/10"
      />
      <RiskSection
        level="Low"
        clauses={lowRiskClauses}
        color="bg-green-500 text-white"
        borderColor="border-green-500"
        bgColor="bg-green-500/10"
      />
    </div>
  );
}
