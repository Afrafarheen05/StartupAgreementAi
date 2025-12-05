import React, { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Award, Target } from 'lucide-react';
import { api } from '../utils/api';

export default function BenchmarkPage() {
  const [benchmarkResult, setbenchmarkResult] = useState(null);
  const [trends, setTrends] = useState(null);
  const [startupType, setStartupType] = useState('SaaS');
  const [fundingStage, setFundingStage] = useState('Series A');
  const [loading, setLoading] = useState(false);

  const handleBenchmark = async () => {
    const currentJobId = sessionStorage.getItem('currentJobId');
    const analysisId = currentJobId || sessionStorage.getItem('currentAnalysisId');
    
    if (!analysisId) {
      alert('⚠️ No document analyzed yet!\n\nPlease upload and analyze a document first from the Upload page.');
      return;
    }

    // Check if backend is running
    try {
      const healthCheck = await fetch('http://localhost:8000/');
      if (!healthCheck.ok) {
        alert('⚠️ Backend server is not running!\n\nPlease start it:\n\n1. Open terminal\n2. cd backend\n3. python -m uvicorn app.main:app --reload');
        return;
      }
    } catch (error) {
      alert('⚠️ Backend server is not running!\n\nPlease start it:\n\n1. Open terminal\n2. cd backend\n3. python -m uvicorn app.main:app --reload');
      return;
    }

    setLoading(true);
    try {
      const result = await api.benchmarkDocument(analysisId, startupType, fundingStage);
      setbenchmarkResult(result);
    } catch (error) {
      console.error('Benchmarking failed:', error);
      alert(`Benchmarking failed: ${error.message}\n\nMake sure you have uploaded and analyzed a document first.`);
    } finally {
      setLoading(false);
    }
  };

  const loadTrends = async () => {
    try {
      const result = await api.getIndustryTrends(startupType, fundingStage);
      setTrends(result);
    } catch (error) {
      console.error('Failed to load trends:', error);
    }
  };

  useEffect(() => {
    loadTrends();
  }, [startupType, fundingStage]);

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-8 mb-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Market Benchmark Analysis</h1>
        <p className="text-purple-100">Compare your terms against 10,000+ real agreements</p>
      </div>

      {/* Configuration */}
      <div className="glass-card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Startup Type</label>
            <select
              value={startupType}
              onChange={(e) => setStartupType(e.target.value)}
              className="w-full bg-white/10 border border-white/20 rounded-lg p-2 text-white focus:ring-2 focus:ring-purple-500"
            >
              <option className="bg-gray-800">SaaS</option>
              <option className="bg-gray-800">Fintech</option>
              <option className="bg-gray-800">Biotech</option>
              <option className="bg-gray-800">E-commerce</option>
              <option className="bg-gray-800">AI/ML</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Funding Stage</label>
            <select
              value={fundingStage}
              onChange={(e) => setFundingStage(e.target.value)}
              className="w-full bg-white/10 border border-white/20 rounded-lg p-2 text-white focus:ring-2 focus:ring-purple-500"
            >
              <option className="bg-gray-800">Pre-seed</option>
              <option className="bg-gray-800">Seed</option>
              <option className="bg-gray-800">Series A</option>
              <option className="bg-gray-800">Series B</option>
              <option className="bg-gray-800">Series C+</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleBenchmark}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 font-semibold transition-all"
            >
              {loading ? 'Analyzing...' : 'Benchmark Document'}
            </button>
          </div>
        </div>
      </div>

      {/* Benchmark Results */}
      {benchmarkResult && (
        <>
          {/* Summary Card */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6 mb-6 border-l-4 border-blue-500">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Overall Market Score</div>
                <div className="text-3xl font-bold text-blue-600">
                  {benchmarkResult.summary.overall_market_score}
                </div>
                <div className="text-sm font-medium text-gray-700">
                  {benchmarkResult.summary.rating}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Clauses Benchmarked</div>
                <div className="text-3xl font-bold text-gray-900">
                  {benchmarkResult.summary.total_clauses_benchmarked}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Founder-Friendly</div>
                <div className="text-3xl font-bold text-green-600">
                  {benchmarkResult.summary.founder_friendly_clauses}
                </div>
                <div className="text-sm text-gray-600">
                  {((benchmarkResult.summary.founder_friendly_clauses / benchmarkResult.summary.total_clauses_benchmarked) * 100).toFixed(0)}% of total
                </div>
              </div>
              <div className="flex items-center justify-center">
                <Award className={`w-16 h-16 ${
                  benchmarkResult.summary.rating === 'Excellent' ? 'text-green-500' :
                  benchmarkResult.summary.rating === 'Good' ? 'text-blue-500' :
                  benchmarkResult.summary.rating === 'Fair' ? 'text-yellow-500' :
                  'text-red-500'
                }`} />
              </div>
            </div>
          </div>

          {/* Clause-by-Clause Benchmarks */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Clause-by-Clause Market Position
            </h3>
            <div className="space-y-4">
              {benchmarkResult.benchmarked_clauses.map((clause, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900">{clause.clause_type}</h4>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      clause.is_founder_friendly ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {clause.is_founder_friendly ? '👍 Founder-Friendly' : '⚠️ Investor-Favoring'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                    <div>
                      <div className="text-sm text-gray-600 mb-2">Your Value</div>
                      <div className="text-lg font-bold text-gray-900">{clause.your_value}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-2">Market Median</div>
                      <div className="text-lg font-medium text-gray-700">{clause.market_data.median}</div>
                    </div>
                  </div>

                  {/* Percentile Bar */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                      <span>Market Position</span>
                      <span className="font-semibold">
                        {clause.your_percentile}th percentile
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                      <div
                        className={`h-full ${
                          clause.your_percentile <= 25 ? 'bg-green-500' :
                          clause.your_percentile <= 50 ? 'bg-blue-500' :
                          clause.your_percentile <= 75 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${clause.your_percentile}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Better ←</span>
                      <span>→ Worse</span>
                    </div>
                  </div>

                  <div className="text-sm text-gray-700 mb-2">
                    <strong>Market Data:</strong> 25th: {clause.market_data['25th_percentile']} | 
                    50th: {clause.market_data.median} | 
                    75th: {clause.market_data['75th_percentile']}
                  </div>

                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-sm font-medium text-gray-900 mb-1">Assessment:</div>
                    <div className="text-sm text-gray-700">{clause.comparison}</div>
                    {clause.recommendations && clause.recommendations.length > 0 && (
                      <div className="mt-2 text-sm text-blue-700">
                        💡 {clause.recommendations[0]}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Intelligence */}
          <div className="bg-purple-50 rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-purple-600" />
              Market Intelligence
            </h3>
            <div className="space-y-3">
              {benchmarkResult.market_intelligence.insights.map((insight, idx) => (
                <div key={idx} className="bg-white p-4 rounded-lg border-l-4 border-purple-400">
                  <p className="text-gray-800">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Industry Trends */}
      {trends && !benchmarkResult && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4">
            Current Market Trends - {trends.startup_type} {trends.funding_stage}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {trends.trends.map((trend, idx) => (
              <div key={idx} className="border rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">{trend.clause_type}</h4>
                <div className="text-sm text-gray-700 space-y-1">
                  <div>Market Standard: <span className="font-medium">{trend.market_standard}</span></div>
                  <div>Typical Range: {trend.typical_range.min} - {trend.typical_range.max}</div>
                  <div>Frequency: <span className="font-medium">{trend.frequency}%</span> of deals</div>
                  <div className="mt-2 text-xs text-blue-700 italic">{trend.recommendation}</div>
                </div>
              </div>
            ))}
          </div>

          {trends.key_insights && (
            <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <h4 className="font-semibold text-blue-900 mb-2">Key Market Insights:</h4>
              <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                {trends.key_insights.map((insight, idx) => (
                  <li key={idx}>{insight}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
