import React from "react";
import { Shield, TrendingDown, AlertCircle, CheckCircle, BarChart } from "lucide-react";

export default function OverallRiskScore({ riskAssessment, sectorInsights }) {
  if (!riskAssessment) return null;

  const { overallScore, rating, breakdown, comparison = {}, verdict } = riskAssessment;

  // Color based on score (0-100, lower is riskier)
  const getScoreColor = (score) => {
    if (score >= 70) return { bg: "from-green-500 to-emerald-600", text: "text-green-400", border: "border-green-500" };
    if (score >= 50) return { bg: "from-yellow-500 to-amber-600", text: "text-yellow-400", border: "border-yellow-500" };
    if (score >= 30) return { bg: "from-orange-500 to-red-600", text: "text-orange-400", border: "border-orange-500" };
    return { bg: "from-red-600 to-red-700", text: "text-red-400", border: "border-red-500" };
  };

  const scoreColors = getScoreColor(overallScore);

  // Rating badge
  const getRatingInfo = (rating) => {
    if (rating === "Startup-Friendly") return { icon: CheckCircle, color: "from-green-500 to-green-600", textColor: "text-green-400" };
    if (rating === "Balanced") return { icon: Shield, color: "from-blue-500 to-blue-600", textColor: "text-blue-400" };
    return { icon: AlertCircle, color: "from-red-500 to-red-600", textColor: "text-red-400" };
  };

  const ratingInfo = getRatingInfo(rating);
  const RatingIcon = ratingInfo.icon;

  return (
    <div className="glass-card">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <Shield className="w-6 h-6 text-purple-400" />
        Overall Risk Assessment
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Main Score Card */}
        <div className="relative p-6 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border-2 border-gray-700">
          <div className="text-center">
            <div className="mb-4">
              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br ${scoreColors.bg} shadow-2xl relative`}>
                <div className="absolute inset-2 rounded-full bg-gray-900 flex items-center justify-center">
                  <span className="text-5xl font-bold text-white">{overallScore}</span>
                </div>
              </div>
            </div>
            
            <div className="mb-3">
              <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${ratingInfo.color} text-white font-semibold text-lg shadow-lg`}>
                <RatingIcon className="w-5 h-5" />
                {rating}
              </span>
            </div>
            
            <p className="text-gray-400 text-sm">Founder Protection Score (out of 100)</p>
          </div>
        </div>

        {/* Risk Breakdown */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Breakdown</h3>
          
          {Object.entries(breakdown).map(([key, value]) => {
            const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()).replace('Risk', '');
            const barColor = value >= 70 ? 'bg-red-500' : value >= 50 ? 'bg-orange-500' : value >= 30 ? 'bg-yellow-500' : 'bg-green-500';
            
            return (
              <div key={key}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-300">{label}</span>
                  <span className={`text-sm font-semibold ${value >= 70 ? 'text-red-400' : value >= 50 ? 'text-orange-400' : 'text-yellow-400'}`}>
                    {value}%
                  </span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${barColor} transition-all duration-500`}
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Verdict */}
      <div className={`p-4 rounded-lg border-2 ${scoreColors.border} bg-gradient-to-r ${scoreColors.bg} bg-opacity-10 mb-6`}>
        <h3 className={`text-lg font-bold ${scoreColors.text} mb-2`}>Verdict</h3>
        <p className="text-white text-sm leading-relaxed">{verdict}</p>
      </div>

      {/* Comparison with Market Standards */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <BarChart className="w-5 h-5 text-blue-400" />
          Comparison with Market Standards
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {comparison && Object.entries(comparison).map(([key, value]) => {
            const label = key.replace('vs', 'vs.').replace(/([A-Z])/g, ' $1').trim();
            const isPositive = value > 0;
            
            return (
              <div 
                key={key}
                className={`p-4 rounded-lg border ${
                  isPositive 
                    ? 'bg-green-500/10 border-green-500/30' 
                    : 'bg-red-500/10 border-red-500/30'
                }`}
              >
                <div className="text-sm text-gray-400 mb-1">{label}</div>
                <div className={`text-2xl font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {isPositive ? '+' : ''}{value}
                </div>
                <div className="text-xs text-gray-500">points {isPositive ? 'better' : 'worse'}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sector-Specific Insights */}
      {sectorInsights && (
        <div className="pt-6 border-t border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">
            Industry Benchmarks ({sectorInsights.benchmarks ? 'Your Sector' : 'General'})
          </h3>
          
          {sectorInsights.benchmarks && (
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
                <div className="text-xs text-gray-400 mb-1">Typical Valuation</div>
                <div className="text-lg font-bold text-blue-400">
                  {sectorInsights.benchmarks.typicalValuation}
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                <div className="text-xs text-gray-400 mb-1">Standard Equity</div>
                <div className="text-lg font-bold text-purple-400">
                  {sectorInsights.benchmarks.equityGiveaway}
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-pink-500/10 border border-pink-500/30">
                <div className="text-xs text-gray-400 mb-1">Next Round</div>
                <div className="text-lg font-bold text-pink-400">
                  {sectorInsights.benchmarks.timeToNextRound}
                </div>
              </div>
            </div>
          )}
          
          {sectorInsights.keyRisks && sectorInsights.keyRisks.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-400 mb-3">Industry-Specific Risks</h4>
              <div className="space-y-2">
                {sectorInsights.keyRisks.map((risk, idx) => (
                  <div key={idx} className="flex items-start gap-2 p-3 rounded-lg bg-gray-800/50">
                    <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-gray-300">{risk}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
