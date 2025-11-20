import React from "react";
import { AlertTriangle, TrendingDown, Clock } from "lucide-react";

const RISK_COLORS = {
  Critical: "from-red-600 to-red-700",
  High: "from-orange-500 to-orange-600",
  Medium: "from-yellow-500 to-yellow-600",
  Low: "from-blue-500 to-blue-600"
};

const PROBABILITY_COLOR = (prob) => {
  if (prob >= 70) return "text-red-400";
  if (prob >= 50) return "text-orange-400";
  if (prob >= 30) return "text-yellow-400";
  return "text-green-400";
};

export default function FuturePrediction({ predictions }) {
  if (!predictions) return null;

  const { timeline = [], overallOutlook = {} } = predictions;

  return (
    <div className="glass-card">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
            <Clock className="w-6 h-6 text-purple-400" />
            Future Risk Predictions
          </h2>
          <p className="text-gray-300">
            Based on ML analysis of 2,500+ similar agreements and historical founder outcomes
          </p>
        </div>
        
        <div className="text-right">
          <div className="text-3xl font-bold text-red-400">{overallOutlook.probability}%</div>
          <div className="text-sm text-gray-400">Risk Probability</div>
        </div>
      </div>

      {/* Overall Outlook Alert */}
      <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-red-400 mb-1">
              {overallOutlook.sentiment} Agreement
            </h3>
            <p className="text-gray-300 text-sm">{overallOutlook.summary}</p>
          </div>
        </div>
      </div>

      {/* Timeline of Risks */}
      <div className="space-y-6">
        {timeline.map((period, idx) => (
          <div key={idx} className="relative">
            {/* Timeline connector */}
            {idx < timeline.length - 1 && (
              <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 to-transparent" />
            )}
            
            <div className="flex gap-4">
              {/* Timeline dot */}
              <div className="relative flex-shrink-0">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/50 z-10 relative">
                  <Clock className="w-6 h-6 text-white" />
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 pb-6">
                <h3 className="text-xl font-bold text-white mb-3">{period.period}</h3>
                
                <div className="space-y-3">
                  {(period.risks || []).map((risk, riskIdx) => (
                    <div 
                      key={riskIdx}
                      className="p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-gray-600 transition-all"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="text-lg font-semibold text-white flex-1">
                          {risk.title}
                        </h4>
                        
                        <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                          {/* Probability Badge */}
                          <div className="text-right">
                            <div className={`text-2xl font-bold ${PROBABILITY_COLOR(risk.probability)}`}>
                              {risk.probability}%
                            </div>
                            <div className="text-xs text-gray-500">probability</div>
                          </div>
                          
                          {/* Impact Badge */}
                          <span className={`
                            px-3 py-1 rounded-full text-xs font-semibold
                            bg-gradient-to-r ${RISK_COLORS[risk.impact]}
                            text-white shadow-lg
                          `}>
                            {risk.impact}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {risk.description}
                      </p>
                      
                      {/* Visual probability bar */}
                      <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r ${
                            risk.probability >= 70 ? 'from-red-500 to-red-600' :
                            risk.probability >= 50 ? 'from-orange-500 to-orange-600' :
                            risk.probability >= 30 ? 'from-yellow-500 to-yellow-600' :
                            'from-green-500 to-green-600'
                          }`}
                          style={{ width: `${risk.probability}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Warning */}
      <div className="mt-6 p-4 rounded-lg bg-gradient-to-r from-amber-500/10 to-red-500/10 border border-amber-500/30">
        <div className="flex items-center gap-2 mb-2">
          <TrendingDown className="w-5 h-5 text-amber-400" />
          <h3 className="text-lg font-semibold text-amber-400">Action Required</h3>
        </div>
        <p className="text-gray-300 text-sm">
          These predictions are based on pattern analysis of similar agreements. 
          <span className="text-white font-semibold"> We strongly recommend reviewing critical clauses</span> with a legal advisor before signing.
        </p>
      </div>
    </div>
  );
}
