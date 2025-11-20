import React, { useEffect, useState } from "react";
import { analyzeAgreement } from "../utils/api";
import { useNavigate } from "react-router-dom";
import OverallRiskScore from "../components/OverallRiskScore";
import DangerousClausesReport from "../components/DangerousClausesReport";
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
      sessionStorage.setItem("analysis", JSON.stringify(result));
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Complete Risk Analysis Report</h1>
          <p className="text-gray-400">
            AI-powered analysis of your {analysisData.metadata?.startupType} agreement at {analysisData.metadata?.fundingStage} stage
          </p>
        </div>
        <PDFDownloadButton data={analysisData} />
      </div>

      {/* Overall Risk Score - Most Important, Show First */}
      <OverallRiskScore 
        riskAssessment={analysisData.riskAssessment} 
        sectorInsights={analysisData.sectorInsights}
      />

      {/* Future Risk Predictions */}
      <FuturePrediction predictions={analysisData.futurePredictions} />

      {/* Dangerous Clauses Report */}
      <DangerousClausesReport clauses={analysisData.clauses} />

      {/* AI Recommendations */}
      <RecommendationsPanel recommendations={analysisData.recommendations} />

      {/* Detailed Clause Table */}
      <div className="glass-card">
        <h2 className="text-2xl font-bold text-white mb-4">All Clauses (Detailed View)</h2>
        <ClauseTable clauses={clauses} onSelect={goToClause} />
      </div>

      {/* Summary Stats */}
      <div className="glass-card">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-lg bg-gray-800/50">
            <div className="text-2xl font-bold text-white">{analysisData.summary.total}</div>
            <div className="text-sm text-gray-400">Total Clauses</div>
          </div>
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <div className="text-2xl font-bold text-red-400">{analysisData.summary.high}</div>
            <div className="text-sm text-gray-400">High Risk</div>
          </div>
          <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <div className="text-2xl font-bold text-yellow-400">{analysisData.summary.medium}</div>
            <div className="text-sm text-gray-400">Medium Risk</div>
          </div>
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <div className="text-2xl font-bold text-green-400">{analysisData.summary.low}</div>
            <div className="text-sm text-gray-400">Low Risk</div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
        <p className="text-sm text-gray-300">
          <strong className="text-amber-400">Legal Disclaimer:</strong> This analysis is powered by AI and machine learning models for informational purposes only. 
          It should not be considered legal advice. Always consult with a qualified attorney before signing any legal agreement.
        </p>
      </div>
    </div>
  );
}
