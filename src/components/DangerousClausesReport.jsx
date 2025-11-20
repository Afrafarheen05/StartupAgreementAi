import React, { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import RiskBadge from "./RiskBadge";

export default function DangerousClausesReport({ clauses }) {
  const [expandedId, setExpandedId] = useState(null);

  if (!clauses || clauses.length === 0) return null;

  // Sort by risk level
  const riskOrder = { High: 0, Medium: 1, Low: 2 };
  const sortedClauses = [...clauses].sort((a, b) => 
    riskOrder[a.risk] - riskOrder[b.risk]
  );

  const dangerousClauses = sortedClauses.filter(c => c.risk === "High" || c.risk === "Medium");
  const safeClauses = sortedClauses.filter(c => c.risk === "Low");

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-pink-600 flex items-center justify-center shadow-lg">
          <AlertTriangle className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Dangerous Clauses Found</h2>
          <p className="text-gray-300 text-sm">
            {dangerousClauses.length} clauses require immediate attention
          </p>
        </div>
      </div>

      {/* Dangerous Clauses */}
      <div className="space-y-3 mb-6">
        {dangerousClauses.map((clause) => (
          <div 
            key={clause.id}
            className="border border-gray-700 rounded-lg overflow-hidden hover:border-gray-600 transition-all"
          >
            {/* Header - Always Visible */}
            <div 
              className="p-4 bg-gray-800/50 cursor-pointer flex items-center justify-between"
              onClick={() => toggleExpand(clause.id)}
            >
              <div className="flex items-center gap-4 flex-1">
                <RiskBadge risk={clause.risk} />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white">{clause.type}</h3>
                  <p className="text-sm text-gray-400 line-clamp-1">{clause.explanation}</p>
                </div>
              </div>
              
              <button className="ml-4 p-2 hover:bg-gray-700 rounded-lg transition-colors">
                {expandedId === clause.id ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>
            </div>

            {/* Expandable Details */}
            {expandedId === clause.id && (
              <div className="p-4 bg-gray-900/30 border-t border-gray-700">
                {/* Clause Text */}
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">CLAUSE TEXT</h4>
                  <p className="text-gray-300 text-sm italic bg-gray-800/50 p-3 rounded-lg border-l-4 border-blue-500">
                    "{clause.text}"
                  </p>
                </div>

                {/* Explanation */}
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">WHY THIS IS RISKY</h4>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    {clause.explanation}
                  </p>
                </div>

                {/* Future Impact */}
                {clause.futureImpact && (
                  <div className="mb-4 p-4 rounded-lg bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30">
                    <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      FUTURE IMPACT (2-3 YEARS)
                    </h4>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {clause.futureImpact}
                    </p>
                  </div>
                )}

                {/* Recommendation */}
                {clause.recommendation && (
                  <div className="p-4 rounded-lg bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/30">
                    <h4 className="text-sm font-semibold text-green-400 mb-2">
                      ✓ RECOMMENDED ACTION
                    </h4>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {clause.recommendation}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Safe Clauses Summary */}
      {safeClauses.length > 0 && (
        <div className="pt-6 border-t border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            Low Risk Clauses ({safeClauses.length})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {safeClauses.map((clause) => (
              <div 
                key={clause.id}
                className="p-3 rounded-lg bg-green-500/5 border border-green-500/20 hover:border-green-500/40 transition-all cursor-pointer"
                onClick={() => toggleExpand(clause.id)}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-white">{clause.type}</span>
                  <RiskBadge risk={clause.risk} />
                </div>
                <p className="text-xs text-gray-400 line-clamp-2">{clause.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
          <div className="text-2xl font-bold text-red-400">
            {clauses.filter(c => c.risk === "High").length}
          </div>
          <div className="text-sm text-gray-400">High Risk</div>
        </div>
        
        <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          <div className="text-2xl font-bold text-yellow-400">
            {clauses.filter(c => c.risk === "Medium").length}
          </div>
          <div className="text-sm text-gray-400">Medium Risk</div>
        </div>
        
        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
          <div className="text-2xl font-bold text-green-400">
            {clauses.filter(c => c.risk === "Low").length}
          </div>
          <div className="text-sm text-gray-400">Low Risk</div>
        </div>
      </div>
    </div>
  );
}
