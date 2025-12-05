import React, { useEffect, useState } from "react";
import RiskBadge from "../components/RiskBadge";
import { AlertTriangle, Lightbulb, TrendingUp, Clock } from "lucide-react";

export default function ClauseDetailsPage() {
  const [clause, setClause] = useState(null);
  const [showFullText, setShowFullText] = useState(false);

  useEffect(() => {
    const c = sessionStorage.getItem("selectedClause");
    if (c) setClause(JSON.parse(c));
  }, []);

  if (!clause)
    return <div className="text-gray-300 text-lg">No clause selected.</div>;

  const displayText = showFullText || !clause.text || clause.text.length <= 500 
    ? clause.text 
    : clause.text.substring(0, 500) + "...";

  return (
    <div className="space-y-6">
      {/* Main Clause Card */}
      <div className="glass-card">
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-3xl font-bold text-white">{clause.type}</h1>
          <RiskBadge risk={clause.risk_level || clause.risk} />
        </div>

        {/* Clause Text */}
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">CLAUSE TEXT</h3>
          <p className="text-gray-300 whitespace-pre-line leading-relaxed">{displayText}</p>
          {clause.text && clause.text.length > 500 && (
            <button
              onClick={() => setShowFullText(!showFullText)}
              className="mt-3 text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              {showFullText ? "Show Less" : "Show Full Text"}
            </button>
          )}
        </div>
      </div>

      {/* Why This Is Risky */}
      <div className="glass-card">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="w-6 h-6 text-red-400" />
          <h2 className="text-2xl font-bold text-white">WHY THIS IS RISKY</h2>
        </div>
        
        <div className="bg-red-500/10 rounded-lg p-4 border border-red-500/30">
          <p className="text-gray-300 leading-relaxed">
            {clause.explanation || `This ${clause.type} clause contains terms that require careful legal review.`}
          </p>
        </div>
        
        {/* Detected Problematic Terms */}
        {((clause.detected_terms && clause.detected_terms.length > 0) || (clause.key_terms && clause.key_terms.length > 0)) && (
          <div className="mt-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">🚩 DETECTED PROBLEMATIC TERMS</h3>
            <div className="flex flex-wrap gap-2">
              {[...(clause.detected_terms || []), ...(clause.key_terms || [])].map((term, idx) => (
                <span key={idx} className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-sm border border-red-500/30 font-mono">
                  "{term}"
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Specific Concerns */}
        {clause.specific_concerns && clause.specific_concerns.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">⚠️ SPECIFIC CONCERNS IDENTIFIED</h3>
            <div className="space-y-2">
              {clause.specific_concerns.map((concern, idx) => (
                <div key={idx} className="flex items-start gap-2 p-2 rounded bg-red-500/10 border border-red-500/20">
                  <span className="text-red-400 text-lg">•</span>
                  <p className="text-gray-300 text-sm">{concern}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Future Impact */}
      <div className="glass-card">
        <div className="flex items-center gap-3 mb-4">
          <Clock className="w-6 h-6 text-orange-400" />
          <h2 className="text-2xl font-bold text-white">FUTURE IMPACT (2-3 YEARS)</h2>
        </div>
        
        <div className="bg-orange-500/10 rounded-lg p-4 border border-orange-500/30">
          <p className="text-gray-300 leading-relaxed">
            {clause.futureImpact || clause.expected_impact || generateFutureImpact(clause)}
          </p>
        </div>
      </div>

      {/* Recommended Action */}
      <div className="glass-card">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="w-6 h-6 text-green-400" />
          <h2 className="text-2xl font-bold text-white">RECOMMENDED ACTION</h2>
        </div>
        
        <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/30 mb-4">
          <p className="text-gray-300 leading-relaxed font-medium">
            {clause.recommendation || generateRecommendation(clause)}
          </p>
        </div>
        
        {/* Negotiation Tips - Use REAL data from backend */}
        {clause.negotiation_tips && clause.negotiation_tips.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white">💡 Negotiation Strategy:</h3>
            {clause.negotiation_tips.map((tip, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-bold text-green-400">{idx + 1}</span>
                </div>
                <p className="text-gray-300 text-sm flex-1">{tip}</p>
              </div>
            ))}
          </div>
        )}
        
        {/* Fallback to generated steps if no real data */}
        {(!clause.negotiation_tips || clause.negotiation_tips.length === 0) && (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white">Specific Actions:</h3>
            {generateActionSteps(clause).map((step, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-bold text-green-400">{idx + 1}</span>
                </div>
                <p className="text-gray-300 text-sm flex-1">{step}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Helper functions for generating content
function generateFutureImpact(clause) {
  const impacts = {
    "Board Control": "If investors have board majority, within 2-3 years they may force strategic pivots, replace the CEO, or push for an acquisition you don't want. Historical data shows 65% of founder-CEOs are replaced when investors control the board.",
    "Liquidation Preference": "In a typical exit scenario (2-3 years), this liquidation preference structure means investors will take their share first. If the preference is 2x or higher with participation, founders may receive less than 10% of what their ownership percentage suggests.",
    "Anti-Dilution": "If you need to raise a down round in 1-2 years (common in challenging markets), this anti-dilution clause will trigger. With full ratchet, founders could lose 20-40% additional equity. This makes future fundraising extremely difficult.",
    "Vesting": "If you're removed or choose to leave before vesting completes (typically 4 years), you'll forfeit unvested shares. In an acquisition within 2-3 years, without acceleration clauses, you could lose millions in equity value.",
    "IP Assignment": "This broad IP assignment could prevent you from using similar technology in future ventures. If this startup fails in 2-3 years, you may be legally restricted from starting a new company in the same space.",
    "Drag-Along Rights": "Investors can force a sale within 2-3 years to return capital to their fund, even if company valuations could be 5-10x higher in 5 years. You'll have no choice but to sell at their preferred timing.",
    "Voting Rights": "Investor veto rights will slow down operations significantly. Every major decision (hires, partnerships, expenditures) will require investor approval, reducing your ability to move quickly and compete effectively."
  };
  
  return impacts[clause.type] || `This ${clause.type} clause will have compounding effects over time, potentially limiting your flexibility and economic outcomes in future fundraising rounds or exit scenarios.`;
}

function generateRecommendation(clause) {
  const recommendations = {
    "Board Control": "Negotiate for balanced board composition: 2 founder seats, 1-2 investor seats, and 1-2 independent directors. Ensure founders retain veto power on critical decisions like CEO removal, company sale, and IP transfers.",
    "Liquidation Preference": "Negotiate to 1x non-participating liquidation preference. This is market standard and fair. Offer to accept 1.5x as absolute maximum compromise, but push hard for 1x.",
    "Anti-Dilution": "Change from full ratchet to broad-based weighted average anti-dilution. Add carve-outs for option pool increases and small insider rounds. This is non-negotiable for founder protection.",
    "Vesting": "Add single-trigger acceleration for 25-50% of shares upon acquisition. Include double-trigger acceleration for remaining shares if role/compensation changes post-acquisition.",
    "IP Assignment": "Add Schedule A listing all prior inventions and side projects that are excluded. Define 'company business' narrowly. Add provision allowing unrelated side projects with board approval.",
    "Drag-Along Rights": "Add minimum price floor: sale price must be at least 2x last round valuation OR $50M minimum. Require founder approval for sales below certain thresholds.",
    "Voting Rights": "Limit investor veto rights to: (1) sale of company, (2) changes to charter/bylaws, (3) IP sales, (4) dissolution. Remove veto from operational decisions."
  };
  
  return recommendations[clause.type] || `Consult with a startup attorney experienced in venture financing to negotiate more balanced terms for this ${clause.type} clause.`;
}

function generateActionSteps(clause) {
  const steps = {
    "Board Control": [
      "Draft a counter-proposal with balanced board structure (2-1-2 or 2-2-1 composition)",
      "Research 3-5 comparable deals in your industry to show market standards",
      "Schedule a call with your attorney to review protective provisions",
      "Present financial projections showing how founder-led companies outperform"
    ],
    "Liquidation Preference": [
      "Request term sheet revision changing to 1x non-participating",
      "Model exit scenarios showing how current terms impact founder returns",
      "Offer other concessions (board seat, information rights) in exchange for better preference",
      "Get competitive term sheets to create negotiating leverage"
    ],
    "Anti-Dilution": [
      "Request replacement of full ratchet with broad-based weighted average",
      "Add carve-outs for option pool increases (up to 20% of fully-diluted)",
      "Include exemption for small insider rounds (<$500K)",
      "Show data on how full ratchet prevents future fundraising"
    ],
    "Vesting": [
      "Propose single-trigger acceleration for 50% on acquisition",
      "Add double-trigger for remaining 50% (acquisition + termination without cause)",
      "Request partial immediate vesting of 6-12 months for founders",
      "Include acceleration upon material change in role or compensation"
    ],
    "IP Assignment": [
      "Create detailed Schedule A of all prior inventions and work",
      "Define 'company business' to exclude unrelated fields",
      "Add provision allowing side projects in different verticals",
      "Exclude general knowledge and skills from assignment"
    ]
  };
  
  return steps[clause.type] || [
    "Schedule consultation with startup attorney familiar with venture deals",
    "Research market standards for this clause in your industry and stage",
    "Draft specific counter-proposal language",
    "Prepare to negotiate with data on founder-friendly alternatives"
  ];
}
