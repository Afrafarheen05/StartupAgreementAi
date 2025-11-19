import React, { useEffect, useState } from "react";
import RiskBadge from "../components/RiskBadge";

export default function ClauseDetailsPage() {
  const [clause, setClause] = useState(null);

  useEffect(() => {
    const c = sessionStorage.getItem("selectedClause");
    if (c) setClause(JSON.parse(c));
  }, []);

  if (!clause)
    return <div className="text-gray-300 text-lg">No clause selected.</div>;

  return (
    <div className="glass-card">
      <div className="flex justify-between items-start">
        <h1 className="text-2xl font-bold text-white">{clause.type}</h1>
        <RiskBadge risk={clause.risk} />
      </div>

      <p className="text-gray-300 mt-4 whitespace-pre-line">{clause.text}</p>

      <div className="mt-6">
        <h3 className="text-xl font-semibold text-white">AI Suggestion</h3>
        <p className="text-purple-300 mt-2">
          This clause may expose founders to certain risks.  
          Consider negotiating a non-participating liquidation preference.
        </p>
      </div>
    </div>
  );
}
