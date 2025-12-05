// Real API - Connects to FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper function for API calls
const apiCall = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API call failed');
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const uploadAgreement = async (file, metadata) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('startup_type', metadata.type || 'SaaS');
    
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    
    const result = await response.json();
    return { 
      success: true, 
      jobId: result.analysis_id.toString(),
      filename: file.name,
      metadata,
      analysisData: result
    };
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};

export const analyzeAgreement = async (jobId, startupType, fundingStage) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${jobId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch analysis');
    }
    
    const data = await response.json();
    
    // First, process recommendations to map them by clause type for easy lookup
    const recommendationsByClause = {};
    (data.recommendations || []).forEach(rec => {
      if (!recommendationsByClause[rec.clause]) {
        recommendationsByClause[rec.clause] = [];
      }
      recommendationsByClause[rec.clause].push(rec);
    });
    
    // Transform backend data to match frontend format WITH real recommendations attached
    const clauses = data.clauses.map((clause, index) => {
      // Find matching recommendations for this clause type
      const matchingRecs = recommendationsByClause[clause.type] || [];
      const primaryRec = matchingRecs[0]; // Get first recommendation for this clause type
      
      return {
        id: index + 1,
        type: clause.type,
        risk: clause.risk_level,
        risk_level: clause.risk_level,
        text: clause.text,
        explanation: clause.explanation,
        key_terms: clause.key_terms || [],
        detected_terms: primaryRec?.detected_terms || [],
        specific_concerns: primaryRec?.specific_concerns || [],
        futureImpact: clause.risk_factors?.join(' ') || primaryRec?.issue || 'Potential impact on future operations',
        recommendation: primaryRec?.recommendation || 'Review with legal advisor',
        negotiation_tips: primaryRec?.negotiation_tips || [],
        expected_impact: primaryRec?.expected_impact || ''
      };
    });
    
    const summary = {
      total: data.risk_assessment.clause_count,
      high: data.risk_assessment.risk_distribution.High,
      medium: data.risk_assessment.risk_distribution.Medium,
      low: data.risk_assessment.risk_distribution.Low,
      typeDistribution: Object.fromEntries(
        Object.entries(data.risk_assessment.clause_types || {}).map(
          ([type, info]) => [type, info.count]
        )
      )
    };
    
    // Transform future predictions - Keep timeline structure intact, NO flatMap
    const futurePredictions = {
      timeline: data.future_predictions?.timeline || [],
      overallOutlook: data.future_predictions?.overall_outlook || {
        probability: 50,
        sentiment: 'Moderate',
        summary: data.risk_assessment.summary
      },
      overall: data.future_predictions?.overall_outlook?.summary || data.risk_assessment.summary
    };
    
    // Transform recommendations - keep all fields for RecommendationsPanel
    const recommendations = (data.recommendations || []).map(rec => ({
      priority: rec.priority,
      clause: rec.clause,
      issue: rec.issue,
      recommendation: rec.recommendation, // Keep original field name
      action: rec.recommendation, // Also map to action for compatibility
      negotiation_tips: rec.negotiation_tips || [],
      negotiationTips: rec.negotiation_tips || [], // camelCase for compatibility
      expected_impact: rec.expected_impact || '',
      impact: rec.expected_impact || '',
      detected_terms: rec.detected_terms || [],
      specific_concerns: rec.specific_concerns || [],
      instances: rec.instances || [],
      clause_snippet: rec.clause_snippet || '',
      full_text: rec.full_text || ''
    }));
    
    // Build risk assessment - use backend data directly (already calculated correctly)
    const riskAssessment = {
      overall_score: data.risk_assessment.overall_score,
      overall_level: data.risk_assessment.overall_level,
      risk_distribution: data.risk_assessment.risk_distribution,
      summary: data.risk_assessment.summary,
      dangerous_clauses: data.risk_assessment.dangerous_clauses || [],
      clause_count: data.risk_assessment.clause_count
    };
    
    // Get filename from sessionStorage or backend
    const filename = sessionStorage.getItem('currentFilename') || data.filename || 'Agreement';
    
    return {
      clauses,
      summary,
      futurePredictions,
      recommendations,
      riskAssessment,  // Main risk data for OverallRiskScore component
      overallRiskScore: data.risk_assessment.overall_score,
      riskLevel: data.risk_assessment.overall_level,
      dangerousClauses: data.risk_assessment.dangerous_clauses,
      sectorInsights: generateSectorInsights(startupType, fundingStage),
      metadata: { startupType, fundingStage },
      filename: filename
    };
    
  } catch (error) {
    console.error('Analysis error:', error);
    throw error;
  }
};

export const askAI = async (prompt, analysisId = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: prompt,
        analysis_id: analysisId
      }),
    });
    
    if (!response.ok) {
      throw new Error('Chat request failed');
    }
    
    const data = await response.json();
    return {
      reply: data.reply || data.response
    };
  } catch (error) {
    console.error('Chat error:', error);
    return {
      reply: "I'm having trouble connecting to the AI service. Please try again."
    };
  }
};

export const trainModel = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/train`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Training failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Training error:', error);
    throw error;
  }
};

export const getClauseDetails = async (analysisId, clauseIndex) => {
  try {
    const clauseId = `${analysisId}:${clauseIndex}`;
    const response = await fetch(`${API_BASE_URL}/api/clause/${clauseId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch clause details');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Clause details error:', error);
    throw error;
  }
};

export const getAnalysesList = async (limit = 10, offset = 0) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/analyses?limit=${limit}&offset=${offset}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch analyses list');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Analyses list error:', error);
    throw error;
  }
};

// Helper function to generate sector-specific insights
function generateSectorInsights(startupType, fundingStage) {
  const insights = {
    fintech: {
      keyRisks: [
        "Regulatory approval rights - investor may block licensing activities",
        "Banking partnership restrictions that could limit growth",
        "Data ownership clauses that prevent platform switching"
      ],
      benchmarks: {
        typicalValuation: fundingStage === 'seed' ? '$3-8M' : fundingStage === 'series-a' ? '$15-40M' : '$1-3M',
        equityGiveaway: fundingStage === 'seed' ? '15-25%' : fundingStage === 'series-a' ? '20-30%' : '10-20%',
        timeToNextRound: '12-18 months'
      }
    },
    healthtech: {
      keyRisks: [
        "HIPAA compliance requirements that investor may control",
        "Clinical trial funding obligations not clearly defined",
        "FDA approval timeline risks not adequately addressed"
      ],
      benchmarks: {
        typicalValuation: fundingStage === 'seed' ? '$4-10M' : fundingStage === 'series-a' ? '$20-50M' : '$1-4M',
        equityGiveaway: fundingStage === 'seed' ? '15-25%' : fundingStage === 'series-a' ? '18-28%' : '10-20%',
        timeToNextRound: '18-24 months'
      }
    },
    agritech: {
      keyRisks: [
        "Seasonal revenue patterns may trigger down-round clauses",
        "Hardware/IoT ownership and IP especially important",
        "Government subsidy dependencies not clearly allocated"
      ],
      benchmarks: {
        typicalValuation: fundingStage === 'seed' ? '$2-6M' : fundingStage === 'series-a' ? '$10-30M' : '$500K-2M',
        equityGiveaway: fundingStage === 'seed' ? '20-30%' : fundingStage === 'series-a' ? '25-35%' : '15-25%',
        timeToNextRound: '12-18 months'
      }
    },
    saas: {
      keyRisks: [
        "ARR/MRR targets that trigger investor control if missed",
        "Customer data ownership could limit platform strategy",
        "Churn-based liquidation triggers are common and dangerous"
      ],
      benchmarks: {
        typicalValuation: fundingStage === 'seed' ? '$4-10M' : fundingStage === 'series-a' ? '$20-60M' : '$1-4M',
        equityGiveaway: fundingStage === 'seed' ? '15-20%' : fundingStage === 'series-a' ? '20-25%' : '10-15%',
        timeToNextRound: '12-18 months'
      }
    },
    default: {
      keyRisks: [
        "Generic agreement may not address industry-specific risks",
        "Milestone definitions may not fit business model",
        "Exit expectations may not align with market dynamics"
      ],
      benchmarks: {
        typicalValuation: fundingStage === 'seed' ? '$3-8M' : fundingStage === 'series-a' ? '$15-40M' : '$1-3M',
        equityGiveaway: fundingStage === 'seed' ? '15-25%' : fundingStage === 'series-a' ? '20-30%' : '10-20%',
        timeToNextRound: '12-18 months'
      }
    }
  };

  return insights[startupType?.toLowerCase()] || insights.default;
}

// Extended API object with new features
export const api = {
  // Original methods
  uploadAgreement,
  analyzeAgreement,
  askAI,
  trainModel,
  getClauseDetails,
  getAnalysesList,
  
  // NEW: Comparison Engine
  compareDocuments: async (analysisIds, comparisonName) => {
    return apiCall('/api/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis_ids: analysisIds, comparison_name: comparisonName })
    });
  },
  
  // NEW: Negotiation Simulator
  startNegotiation: async (clause, investorProfile, fundingStage, startupType) => {
    return apiCall('/api/negotiation/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clause, investor_profile: investorProfile, funding_stage: fundingStage, startup_type: startupType })
    });
  },
  
  makeCounterOffer: async (sessionId, proposal, reasoning) => {
    return apiCall(`/api/negotiation/${sessionId}/counter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proposal, reasoning })
    });
  },
  
  getNegotiationSession: async (sessionId) => {
    return apiCall(`/api/negotiation/${sessionId}`);
  },
  
  // NEW: Compliance Checker
  checkCompliance: async (analysisId, jurisdictions) => {
    return apiCall('/api/compliance/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis_id: analysisId, jurisdictions })
    });
  },
  
  getJurisdictionRequirements: async (jurisdiction) => {
    return apiCall(`/api/compliance/requirements/${jurisdiction}`);
  },
  
  // NEW: Version Control
  createVersion: async (documentId, analysisId, createdBy, changeSummary) => {
    return apiCall('/api/version/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: documentId, analysis_id: analysisId, created_by: createdBy, change_summary: changeSummary })
    });
  },
  
  getVersionHistory: async (documentId) => {
    return apiCall(`/api/version/history/${documentId}`);
  },
  
  compareVersions: async (documentId, versionA, versionB) => {
    return apiCall('/api/version/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: documentId, version_a: versionA, version_b: versionB })
    });
  },
  
  // NEW: Benchmark Engine
  benchmarkDocument: async (analysisId, startupType, fundingStage) => {
    return apiCall('/api/benchmark/document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ analysis_id: analysisId, startup_type: startupType, funding_stage: fundingStage })
    });
  },
  
  getIndustryTrends: async (startupType, fundingStage) => {
    return apiCall(`/api/benchmark/trends?startup_type=${startupType}&funding_stage=${fundingStage}`);
  },
  
  // NEW: Contract Generator
  generateAlternativeClause: async (clause, startupType, fundingStage) => {
    return apiCall('/api/generate/alternative', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clause, startup_type: startupType, funding_stage: fundingStage })
    });
  },
  
  generateCustomAgreement: async (templateName, parameters, customizations) => {
    return apiCall('/api/generate/document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ template_name: templateName, parameters, customizations })
    });
  },
  
  listTemplates: async () => {
    return apiCall('/api/generate/templates');
  }
};

export default api;
