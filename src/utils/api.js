// Fake API (replace later with backend API)

export const uploadAgreement = async (file) => {
  await new Promise(r => setTimeout(r, 1200));
  return { success: true, jobId: "job_" + Date.now() };
};

export const analyzeAgreement = async (jobId) => {
  await new Promise(r => setTimeout(r, 1200));

  const clauses = [
    { id: 1, type: "Liquidation Preference", risk: "High", text: "Investor receives 1x participating liquidation preference..." },
    { id: 2, type: "Vesting", risk: "Low", text: "Founder shares vest over 4 years..." },
    { id: 3, type: "Information Rights", risk: "Medium", text: "Investor receives quarterly financial reports..." },
    { id: 4, type: "IP Assignment", risk: "Low", text: "All founders assign IP to the company..." },
  ];

  const summary = {
    total: clauses.length,
    high: clauses.filter(c=>c.risk==="High").length,
    medium: clauses.filter(c=>c.risk==="Medium").length,
    low: clauses.filter(c=>c.risk==="Low").length,
    typeDistribution: {
      "Liquidation Preference": 1,
      Vesting: 1,
      "Information Rights": 1,
      "IP Assignment": 1,
    }
  };

  return { clauses, summary };
};

export const askAI = async (prompt) => {
  await new Promise(r => setTimeout(r, 800));
  return {
    reply: `AI Analysis: ${prompt}\n\nThis clause may expose the founder to certain risks. Recommend negotiating non-participating preference.`
  };
};
