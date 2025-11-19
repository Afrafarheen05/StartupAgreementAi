import React, { useEffect, useState } from "react";
import { analyzeAgreement } from "../utils/api";
import ClauseTable from "../components/ClauseTable";
import { useNavigate } from "react-router-dom";

export default function AnalysisPage() {
  const navigate = useNavigate();
  const [clauses, setClauses] = useState([]);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const jobId = sessionStorage.getItem("currentJobId");
    if (!jobId) {
      navigate("/upload");
      return;
    }

    (async () => {
      const result = await analyzeAgreement(jobId);
      sessionStorage.setItem("analysis", JSON.stringify(result));
      setClauses(result.clauses);
      setSummary(result.summary);
    })();
  }, []);

  const goToClause = (clause) => {
    sessionStorage.setItem("selectedClause", JSON.stringify(clause));
    navigate(`/clause/${clause.id}`);
  };

  if (!summary)
    return <div className="text-gray-300 text-lg">Analyzing...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Analysis Results</h1>

      <div className="glass-card mb-6">
        <h2 className="text-xl text-white font-semibold mb-2">Summary</h2>

        <p className="text-gray-300">Total Clauses: {summary.total}</p>
        <p className="text-red-400">High Risk: {summary.high}</p>
        <p className="text-yellow-300">Medium Risk: {summary.medium}</p>
        <p className="text-green-400">Low Risk: {summary.low}</p>
      </div>

      <ClauseTable clauses={clauses} onSelect={goToClause} />
    </div>
  );
}
