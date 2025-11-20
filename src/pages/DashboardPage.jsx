import React, { useEffect, useState } from "react";
import ChartRiskPie from "../components/ChartRiskPie";
import ChartClauseTypes from "../components/ChartClauseTypes";
import { TrendingUp, AlertTriangle, Clock, Target } from "lucide-react";

export default function DashboardPage() {
  const [analysisData, setAnalysisData] = useState(null);

  useEffect(() => {
    const saved = sessionStorage.getItem("analysis");
    if (saved) {
      const parsed = JSON.parse(saved);
      setAnalysisData(parsed);
    }
  }, []);

  if (!analysisData)
    return <div className="text-gray-300 text-lg">No analysis available. Please upload and analyze an agreement first.</div>;

  const { summary, riskAssessment, futurePredictions, metadata } = analysisData;

  // Calculate risk trend
  const riskTrend = riskAssessment ? 
    (riskAssessment.overallScore < 40 ? 'Increasing' : riskAssessment.overallScore < 60 ? 'Moderate' : 'Decreasing') 
    : 'Unknown';

  // Get highest priority risks from future predictions
  const topRisks = futurePredictions?.timeline?.[0]?.risks?.slice(0, 3) || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl text-white font-bold mb-2">Risk Dashboard</h1>
        <p className="text-gray-400">
          Comprehensive overview of your {metadata?.startupType || 'startup'} agreement analysis
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Overall Risk Score */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            <span className={`text-2xl font-bold ${
              riskAssessment.overallScore >= 70 ? 'text-green-400' :
              riskAssessment.overallScore >= 50 ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              {riskAssessment.overallScore}/100
            </span>
          </div>
          <h3 className="text-sm font-semibold text-gray-400 mb-1">Protection Score</h3>
          <p className="text-xs text-gray-500">{riskAssessment.rating}</p>
        </div>

        {/* Total Clauses */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">{summary.total}</span>
          </div>
          <h3 className="text-sm font-semibold text-gray-400 mb-1">Total Clauses</h3>
          <p className="text-xs text-gray-500">
            {summary.high} high • {summary.medium} medium • {summary.low} low
          </p>
        </div>

        {/* Risk Trend */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <span className={`text-2xl font-bold ${
              riskTrend === 'Increasing' ? 'text-red-400' :
              riskTrend === 'Moderate' ? 'text-yellow-400' :
              'text-green-400'
            }`}>
              {riskTrend}
            </span>
          </div>
          <h3 className="text-sm font-semibold text-gray-400 mb-1">Risk Trend</h3>
          <p className="text-xs text-gray-500">Based on ML analysis</p>
        </div>

        {/* Future Risk Probability */}
        <div className="glass-card">
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-pink-600 flex items-center justify-center">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold text-red-400">
              {futurePredictions?.overallOutlook?.probability || 0}%
            </span>
          </div>
          <h3 className="text-sm font-semibold text-gray-400 mb-1">Risk Probability</h3>
          <p className="text-xs text-gray-500">Next 3 years</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartRiskPie data={summary} />
        <ChartClauseTypes data={summary.typeDistribution} />
      </div>

      {/* Risk Categories (Operational, Regulatory, Financial) */}
      {riskAssessment?.riskCategories && (
        <div className="glass-card">
          <h2 className="text-xl font-bold text-white mb-4">Risk Categories Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Operational Risk */}
            <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">Operational Legal Risk</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  riskAssessment.riskCategories.operational?.severity === 'High' ? 'bg-red-500 text-white' :
                  riskAssessment.riskCategories.operational?.severity === 'Medium' ? 'bg-yellow-500 text-white' :
                  'bg-green-500 text-white'
                }`}>
                  {riskAssessment.riskCategories.operational?.severity || 'Low'}
                </span>
              </div>
              <p className="text-gray-400 text-sm mb-2">
                Board control, voting rights, management decisions
              </p>
              <div className="text-2xl font-bold text-blue-400">
                {riskAssessment.riskCategories.operational?.count || 0} clauses
              </div>
              {riskAssessment.riskCategories.operational?.clauses?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-blue-500/20">
                  <p className="text-xs text-gray-500 mb-2">High Risk Items:</p>
                  {riskAssessment.riskCategories.operational.clauses.slice(0, 2).map((clause, idx) => (
                    <p key={idx} className="text-xs text-red-400 mb-1">• {clause.type}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Regulatory Risk */}
            <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">Regulatory & Compliance Risk</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  riskAssessment.riskCategories.regulatory?.severity === 'High' ? 'bg-red-500 text-white' :
                  riskAssessment.riskCategories.regulatory?.severity === 'Medium' ? 'bg-yellow-500 text-white' :
                  'bg-green-500 text-white'
                }`}>
                  {riskAssessment.riskCategories.regulatory?.severity || 'Low'}
                </span>
              </div>
              <p className="text-gray-400 text-sm mb-2">
                IP rights, compliance obligations, restrictions
              </p>
              <div className="text-2xl font-bold text-purple-400">
                {riskAssessment.riskCategories.regulatory?.count || 0} clauses
              </div>
              {riskAssessment.riskCategories.regulatory?.clauses?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-purple-500/20">
                  <p className="text-xs text-gray-500 mb-2">High Risk Items:</p>
                  {riskAssessment.riskCategories.regulatory.clauses.slice(0, 2).map((clause, idx) => (
                    <p key={idx} className="text-xs text-red-400 mb-1">• {clause.type}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Financial Risk */}
            <div className="p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/30">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">Financial Investment Risk</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  riskAssessment.riskCategories.financial?.severity === 'High' ? 'bg-red-500 text-white' :
                  riskAssessment.riskCategories.financial?.severity === 'Medium' ? 'bg-yellow-500 text-white' :
                  'bg-green-500 text-white'
                }`}>
                  {riskAssessment.riskCategories.financial?.severity || 'Low'}
                </span>
              </div>
              <p className="text-gray-400 text-sm mb-2">
                Liquidation preference, anti-dilution, valuation
              </p>
              <div className="text-2xl font-bold text-orange-400">
                {riskAssessment.riskCategories.financial?.count || 0} clauses
              </div>
              {riskAssessment.riskCategories.financial?.clauses?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-orange-500/20">
                  <p className="text-xs text-gray-500 mb-2">High Risk Items:</p>
                  {riskAssessment.riskCategories.financial.clauses.slice(0, 2).map((clause, idx) => (
                    <p key={idx} className="text-xs text-red-400 mb-1">• {clause.type}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Risk Breakdown Bars */}
      {riskAssessment?.breakdown && (
        <div className="glass-card">
          <h2 className="text-xl font-bold text-white mb-4">Risk Category Breakdown</h2>
          <div className="space-y-4">
            {Object.entries(riskAssessment.breakdown).map(([key, value]) => {
              const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()).replace('Risk', '');
              const barColor = value >= 70 ? 'bg-red-500' : value >= 50 ? 'bg-orange-500' : value >= 30 ? 'bg-yellow-500' : 'bg-green-500';
              
              return (
                <div key={key}>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-semibold text-white">{label}</span>
                    <span className={`text-sm font-bold ${
                      value >= 70 ? 'text-red-400' : 
                      value >= 50 ? 'text-orange-400' : 
                      value >= 30 ? 'text-yellow-400' : 
                      'text-green-400'
                    }`}>
                      {value}%
                    </span>
                  </div>
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${barColor} transition-all duration-500 relative`}
                      style={{ width: `${value}%` }}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/20" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Immediate Risks */}
      <div className="glass-card">
        <h2 className="text-xl font-bold text-white mb-4">Top Immediate Risks (6-12 months)</h2>
        {topRisks.length > 0 ? (
          <div className="space-y-3">
            {topRisks.map((risk, idx) => (
              <div 
                key={idx}
                className="p-4 rounded-lg bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-white flex-1">{risk.title}</h3>
                  <div className="flex items-center gap-2 ml-4">
                    <span className="text-2xl font-bold text-red-400">{risk.probability}%</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      risk.impact === 'Critical' ? 'bg-red-500 text-white' :
                      risk.impact === 'High' ? 'bg-orange-500 text-white' :
                      'bg-yellow-500 text-white'
                    }`}>
                      {risk.impact}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-300">{risk.description}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No immediate high-risk items identified.</p>
        )}
      </div>

      {/* Market Comparison */}
      {riskAssessment?.comparison && (
        <div className="glass-card">
          <h2 className="text-xl font-bold text-white mb-4">Market Comparison</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(riskAssessment.comparison).map(([key, value]) => {
              const label = key.replace('vs', 'vs.').replace(/([A-Z])/g, ' $1').trim();
              const isPositive = value > 0;
              
              return (
                <div 
                  key={key}
                  className={`p-6 rounded-lg border-2 text-center ${
                    isPositive 
                      ? 'bg-green-500/10 border-green-500/30' 
                      : 'bg-red-500/10 border-red-500/30'
                  }`}
                >
                  <div className="text-sm text-gray-400 mb-2">{label}</div>
                  <div className={`text-4xl font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '+' : ''}{value}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {isPositive ? 'Better than' : 'Worse than'} benchmark
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
