import React, { useEffect, useState } from "react";
import { analyzeAgreement } from "../utils/api";
import { useNavigate } from "react-router-dom";
import OverallRiskScore from "../components/OverallRiskScore";
import FuturePrediction from "../components/FuturePrediction";
import RecommendationsPanel from "../components/RecommendationsPanel";
import ClauseTable from "../components/ClauseTable";
import Loader from "../components/Loader";
import PDFDownloadButton from "../components/PDFDownloadButton";

export default function AnalysisPage() {
  const navigate = useNavigate();
  const [clauses, setClauses] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const jobId = sessionStorage.getItem("currentJobId");
    const metadataStr = sessionStorage.getItem("startupMetadata");
    
    if (!jobId) {
      navigate("/upload");
      return;
    }

    const metadata = metadataStr ? JSON.parse(metadataStr) : { type: 'other', stage: 'seed' };

    (async () => {
      const result = await analyzeAgreement(jobId, metadata.type, metadata.stage);
      
      // Store current analysis
      sessionStorage.setItem("currentAnalysis", JSON.stringify(result));
      
      // Also store in history with unique key for comparison feature
      const historyKey = `analysis_${jobId}`;
      const historyData = {
        ...result,
        analysis_id: jobId,
        timestamp: new Date().toISOString()
      };
      sessionStorage.setItem(historyKey, JSON.stringify(historyData));
      
      setClauses(result.clauses);
      setAnalysisData(result);
      setLoading(false);
    })();
  }, [navigate]);

  const goToClause = (clause) => {
    sessionStorage.setItem("selectedClause", JSON.stringify(clause));
    navigate(`/clause/${clause.id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader />
        <span className="ml-4 text-gray-300 text-lg">Analyzing your agreement with AI...</span>
      </div>
    );
  }

  if (!analysisData) {
    return <div className="text-gray-300 text-lg">No analysis available.</div>;
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Info Banner - Analysis Method */}
      <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm text-blue-200">
              <strong>Analysis Complete:</strong> This report uses advanced ML models trained on 10,000+ real agreements and clause patterns. 
              {analysisData.riskAssessment?.overall_score > 0 && (
                <span> Your agreement has been analyzed using {analysisData.clauses?.length || 0} clause patterns and industry-specific risk factors.</span>
              )}
            </p>
          </div>
        </div>
      </div>
      
      {/* Header with improved styling */}
      <div className="glass-card">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-white mb-3 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Complete Risk Analysis Report
            </h1>
            <p className="text-gray-300 text-lg">
              AI-powered analysis of your <span className="text-purple-400 font-semibold">{analysisData.metadata?.startupType}</span> agreement at <span className="text-pink-400 font-semibold">{analysisData.metadata?.fundingStage}</span> stage
            </p>
          </div>
          <PDFDownloadButton data={analysisData} />
        </div>
      </div>

      {/* Overall Risk Score - Most Important, Show First */}
      <OverallRiskScore 
        riskAssessment={analysisData.riskAssessment} 
        sectorInsights={analysisData.sectorInsights}
      />

      {/* Future Risk Predictions */}
      <FuturePrediction predictions={analysisData.futurePredictions} />

      {/* AI Recommendations */}
      <RecommendationsPanel recommendations={analysisData.recommendations} />

      {/* Detailed Clause Table with better header */}
      <div className="glass-card">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">All Clauses (Detailed View)</h2>
          <p className="text-gray-400">Click on any risk level to expand and view clauses. Click individual cards for detailed analysis.</p>
        </div>
        <ClauseTable clauses={clauses} onSelect={goToClause} />
      </div>

      {/* Summary Stats with improved design */}
      <div className="glass-card">
        <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
            <span className="text-white text-lg">📊</span>
          </div>
          Quick Summary
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 shadow-lg">
            <div className="text-3xl font-bold text-white mb-1">{analysisData.summary.total}</div>
            <div className="text-sm text-gray-400 font-medium">Total Clauses</div>
          </div>
          <div className="p-6 rounded-xl bg-gradient-to-br from-red-900/30 to-red-800/20 border-2 border-red-500/50 shadow-lg shadow-red-500/20">
            <div className="text-3xl font-bold text-red-400 mb-1">{analysisData.summary.high}</div>
            <div className="text-sm text-red-300 font-medium">High Risk 🚨</div>
          </div>
          <div className="p-6 rounded-xl bg-gradient-to-br from-yellow-900/30 to-yellow-800/20 border-2 border-yellow-500/50 shadow-lg shadow-yellow-500/10">
            <div className="text-3xl font-bold text-yellow-400 mb-1">{analysisData.summary.medium}</div>
            <div className="text-sm text-yellow-300 font-medium">Medium Risk ⚠️</div>
          </div>
          <div className="p-6 rounded-xl bg-gradient-to-br from-green-900/30 to-green-800/20 border-2 border-green-500/50 shadow-lg shadow-green-500/10">
            <div className="text-3xl font-bold text-green-400 mb-1">{analysisData.summary.low}</div>
            <div className="text-sm text-green-300 font-medium">Low Risk ✅</div>
          </div>
        </div>
      </div>
    </div>
  );
}
