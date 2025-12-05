import React, { useState } from "react";
import { Lightbulb, ChevronRight, Copy, Check } from "lucide-react";

const PRIORITY_COLORS = {
  Critical: "from-red-600 to-red-700",
  High: "from-orange-500 to-orange-600",
  Medium: "from-yellow-500 to-yellow-600",
  Low: "from-blue-500 to-blue-600"
};

export default function RecommendationsPanel({ recommendations }) {
  const [expandedId, setExpandedId] = useState(0);
  const [copiedId, setCopiedId] = useState(null);

  if (!recommendations || recommendations.length === 0) return null;

  const toggleExpand = (index) => {
    setExpandedId(expandedId === index ? null : index);
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="glass-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-amber-600 flex items-center justify-center shadow-lg">
          <Lightbulb className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">AI-Powered Recommendations</h2>
          <p className="text-gray-300 text-sm">
            Actionable steps to negotiate better terms
          </p>
        </div>
      </div>

      {/* Priority Legend */}
      <div className="flex items-center gap-3 mb-6 p-3 rounded-lg bg-gray-800/50">
        <span className="text-sm text-gray-400">Priority:</span>
        {Object.entries(PRIORITY_COLORS).map(([priority, color]) => (
          <div key={priority} className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full bg-gradient-to-br ${color}`} />
            <span className="text-xs text-gray-300">{priority}</span>
          </div>
        ))}
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec, index) => {
          const isExpanded = expandedId === index;
          const priorityColor = PRIORITY_COLORS[rec.priority];

          return (
            <div 
              key={index}
              className="border border-gray-700 rounded-lg overflow-hidden hover:border-gray-600 transition-all"
            >
              {/* Header */}
              <div 
                className="p-4 bg-gray-800/50 cursor-pointer flex items-start justify-between"
                onClick={() => toggleExpand(index)}
              >
                <div className="flex items-start gap-4 flex-1">
                  {/* Priority Badge */}
                  <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${priorityColor} text-white text-xs font-semibold flex-shrink-0`}>
                    {rec.priority}
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">
                      {rec.clause}
                    </h3>
                    <p className="text-sm text-gray-400">{rec.issue}</p>
                  </div>
                </div>
                
                <ChevronRight 
                  className={`w-5 h-5 text-gray-400 flex-shrink-0 ml-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                />
              </div>

              {/* Expandable Content */}
              {isExpanded && (
                <div className="p-4 bg-gray-900/30 border-t border-gray-700 space-y-4">
                  {/* Show instance count and snippets if multiple */}
                  {rec.instances && rec.instances.length > 1 && (
                    <div className="mb-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
                      <h4 className="text-sm font-semibold text-amber-400 mb-2">
                        ⚠️ {rec.instances.length} instances of this clause found in the document
                      </h4>
                      <div className="space-y-2 mt-3">
                        {rec.instances.map((inst, idx) => (
                          <div key={idx} className="p-2 rounded bg-gray-800/50 border border-gray-700">
                            <span className="text-xs text-gray-500">Instance #{idx + 1}:</span>
                            <p className="text-xs text-gray-400 mt-1">{inst.snippet}...</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Detected Problematic Terms */}
                  {rec.detected_terms && rec.detected_terms.length > 0 && (
                    <div className="mb-3">
                      <h4 className="text-sm font-semibold text-red-400 mb-2">🚨 Detected Problematic Terms:</h4>
                      <div className="flex flex-wrap gap-2">
                        {rec.detected_terms.map((term, idx) => (
                          <span key={idx} className="px-2 py-1 rounded-full bg-red-500/20 text-red-300 text-xs border border-red-500/30">
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Specific Concerns */}
                  {rec.specific_concerns && rec.specific_concerns.length > 0 && (
                    <div className="mb-3">
                      <h4 className="text-sm font-semibold text-orange-400 mb-2">⚠️ Specific Concerns:</h4>
                      <ul className="space-y-1">
                        {rec.specific_concerns.map((concern, idx) => (
                          <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                            <span className="text-orange-400 mt-1">•</span>
                            <span>{concern}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Recommendation */}
                  {rec.recommendation && (
                    <div>
                      <h4 className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                        RECOMMENDED CHANGE
                      </h4>
                      <p className="text-gray-300 text-sm leading-relaxed bg-green-500/5 p-3 rounded-lg border border-green-500/20">
                        {rec.recommendation}
                      </p>
                    </div>
                  )}

                  {/* Negotiation Tips */}
                  {(rec.negotiation_tips || rec.negotiationTips) && (rec.negotiation_tips || rec.negotiationTips).length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-blue-400 mb-3 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                        NEGOTIATION STRATEGY
                      </h4>
                      <div className="space-y-2">
                        {(rec.negotiation_tips || rec.negotiationTips).map((tip, tipIndex) => (
                          <div 
                            key={tipIndex}
                            className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/5 border border-blue-500/20 hover:border-blue-500/40 transition-all group"
                          >
                            <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                              <span className="text-xs font-bold text-blue-400">{tipIndex + 1}</span>
                            </div>
                            <div className="flex-1">
                              <p className="text-sm text-gray-300 leading-relaxed">{tip}</p>
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                copyToClipboard(tip, `${index}-${tipIndex}`);
                              }}
                              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-blue-500/20 rounded"
                            >
                              {copiedId === `${index}-${tipIndex}` ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4 text-gray-400" />
                              )}
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Expected Impact */}
                  {(rec.expected_impact || rec.expectedImpact) && (
                    <div className="p-4 rounded-lg bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                      <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
                        <span className="text-lg">📈</span>
                        EXPECTED IMPACT
                      </h4>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {rec.expected_impact || rec.expectedImpact}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action CTA */}
      <div className="mt-6 p-4 rounded-lg bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/30">
        <h3 className="text-lg font-semibold text-white mb-2">Next Steps</h3>
        <p className="text-gray-300 text-sm mb-3">
          Use these recommendations as talking points with your legal advisor. Most investors respect founders who negotiate intelligently.
        </p>
        <div className="flex gap-3">
          <button 
            onClick={() => window.print()}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-colors"
          >
            Print Report
          </button>
          <button 
            onClick={() => {
              const text = recommendations.map((r, i) => 
                `${i+1}. ${r.clause}\nIssue: ${r.issue}\nRecommendation: ${r.recommendation}\n`
              ).join('\n');
              copyToClipboard(text, 'all');
            }}
            className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-semibold transition-colors flex items-center gap-2"
          >
            {copiedId === 'all' ? (
              <>
                <Check className="w-4 h-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy All
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
