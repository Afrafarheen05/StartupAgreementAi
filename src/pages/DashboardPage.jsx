import React, { useEffect, useState } from "react";
import ChartRiskPie from "../components/ChartRiskPie";
import ChartClauseTypes from "../components/ChartClauseTypes";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const saved = sessionStorage.getItem("analysis");
    if (saved) {
      const parsed = JSON.parse(saved);
      setSummary(parsed.summary);
    }
  }, []);

  if (!summary)
    return <div className="text-gray-300 text-lg">No analysis available.</div>;

  return (
    <div>
      <h1 className="text-2xl text-white font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartRiskPie data={summary} />
        <ChartClauseTypes data={summary.typeDistribution} />
      </div>
    </div>
  );
}
