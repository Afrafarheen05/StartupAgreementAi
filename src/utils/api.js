// Real API - Connects to FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    
    // Transform backend data to match frontend format
    const clauses = data.clauses.map((clause, index) => ({
      id: index + 1,
      type: clause.type,
      risk: clause.risk_level,
      text: clause.text,
      explanation: clause.explanation,
      futureImpact: clause.risk_factors?.join(' ') || 'Potential impact on future operations',
      recommendation: clause.recommendation || 'Review with legal advisor'
    }));
    
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
    
    // Transform future predictions
    const futurePredictions = {
      timeline: (data.future_predictions?.timeline || []).flatMap(period => 
        (period.risks || []).map(risk => ({
          period: period.period,
          probability: risk.probability,
          risk: risk.impact,
          description: risk.description,
          impact: risk.impact,
          title: risk.title
        }))
      ),
      overallOutlook: data.future_predictions?.overall_outlook || {
        probability: 50,
        sentiment: 'Moderate',
        summary: data.risk_assessment.summary
      },
      overall: data.future_predictions?.overall_outlook?.summary || data.risk_assessment.summary
    };
    
    // Transform recommendations
    const recommendations = data.recommendations.map(rec => ({
      priority: rec.priority,
      clause: rec.clause,
      issue: rec.issue,
      action: rec.recommendation,
      tips: rec.negotiation_tips,
      impact: rec.expected_impact
    }));
    
    // Build risk assessment
    const riskAssessment = {
      overallScore: 100 - data.risk_assessment.overall_score, // Invert for frontend
      rating: data.risk_assessment.overall_level,
      riskCategories: data.risk_assessment.risk_categories || {},
      breakdown: {
        controlRisk: data.risk_assessment.risk_distribution.High * 20,
        economicRisk: data.risk_assessment.risk_distribution.High * 15,
        operationalRisk: data.risk_assessment.risk_distribution.Medium * 10,
        exitRisk: data.risk_assessment.risk_distribution.High * 18,
        dilutionRisk: data.risk_assessment.risk_distribution.Medium * 12,
      },
      comparison: {
        vsMarketAverage: Math.round((100 - data.risk_assessment.overall_score) - 60),
        vsStartupFriendly: Math.round((100 - data.risk_assessment.overall_score) - 75),
        vsInvestorFriendly: Math.round((100 - data.risk_assessment.overall_score) - 45)
      },
      verdict: data.risk_assessment.summary
    };
    
    return {
      clauses,
      summary,
      futurePredictions,
      recommendations,
      riskAssessment,
      overallRiskScore: data.risk_assessment.overall_score,
      riskLevel: data.risk_assessment.overall_level,
      dangerousClauses: data.risk_assessment.dangerous_clauses,
      sectorInsights: generateSectorInsights(startupType, fundingStage),
      metadata: { startupType, fundingStage }
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
      reply: data.response
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
