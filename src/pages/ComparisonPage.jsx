import React, { useState, useEffect } from 'react';
import { Upload, TrendingUp, Scale, Trophy, AlertCircle, FileText, CheckCircle, Award } from 'lucide-react';
import { api } from '../utils/api';

export default function ComparisonPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [comparisonName, setComparisonName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  useEffect(() => {
    loadRecentAnalyses();
  }, []);

  const loadRecentAnalyses = () => {
    const analyses = [];
    
    // Try to load current analysis
    const currentJobId = sessionStorage.getItem('currentJobId');
    const currentAnalysis = sessionStorage.getItem('currentAnalysis');
    if (currentAnalysis && currentJobId) {
      try {
        const data = JSON.parse(currentAnalysis);
        analyses.push({
          id: currentJobId,
          filename: data.filename || sessionStorage.getItem('currentFilename') || 'Current Document',
          riskScore: data.overallRiskScore || data.riskAssessment?.overall_score || 0,
          timestamp: data.timestamp || new Date().toISOString()
        });
      } catch (e) {
        console.error('Error loading current analysis:', e);
      }
    }
    
    // Load other analyses from storage
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key && key.startsWith('analysis_') && key !== 'analysis_current') {
        try {
          const data = JSON.parse(sessionStorage.getItem(key));
          analyses.push({
            id: key.replace('analysis_', ''),
            filename: data.filename || `Document ${analyses.length + 1}`,
            riskScore: data.overallRiskScore || data.riskAssessment?.overall_score || 0,
            timestamp: data.timestamp || new Date().toISOString()
          });
        } catch (e) {
          console.error('Error loading analysis:', e);
        }
      }
    }
    
    // Remove duplicates based on id
    const uniqueAnalyses = analyses.filter((item, index, self) =>
      index === self.findIndex((t) => t.id === item.id)
    );
    
    setDocuments(uniqueAnalyses);
  };

  const toggleDocument = (docId) => {
    if (selectedDocs.includes(docId)) {
      setSelectedDocs(selectedDocs.filter(id => id !== docId));
    } else {
      setSelectedDocs([...selectedDocs, docId]);
    }
  };

  const handleCompare = async () => {
    if (selectedDocs.length < 2) {
      alert('Please select at least 2 documents to compare');
      return;
    }

    // Check if backend is running
    try {
      const healthCheck = await fetch('http://localhost:8000/');
      if (!healthCheck.ok) {
        alert('Backend server is not responding. Please start the backend server first:\n\ncd backend\npython -m uvicorn app.main:app --reload');
        return;
      }
    } catch (error) {
      alert('⚠️ Backend server is not running!\n\nPlease start it first:\n\n1. Open a new terminal\n2. cd backend\n3. python -m uvicorn app.main:app --reload');
      return;
    }

    setLoading(true);
    try {
      const result = await api.compareDocuments(selectedDocs, comparisonName || 'Document Comparison');
      setComparisonResult(result);
    } catch (error) {
      console.error('Comparison failed:', error);
      alert(`Comparison failed: ${error.message}\n\nMake sure you have uploaded at least 2 documents and the backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score) => {
    if (score >= 70) return 'text-red-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getRiskBadge = (riskLevel) => {
    if (riskLevel === 'Critical') return 'bg-red-500 text-white';
    if (riskLevel === 'High') return 'bg-orange-500 text-white';
    if (riskLevel === 'Medium') return 'bg-yellow-500 text-white';
    return 'bg-green-500 text-white';
  };

  const handleMultipleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Check if backend is running first
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

    setUploading(true);
    const newProgress = {};
    files.forEach(file => {
      newProgress[file.name] = { status: 'pending', progress: 0 };
    });
    setUploadProgress(newProgress);

    const API_BASE_URL = 'http://localhost:8000';

    // Upload files sequentially to avoid overwhelming the server
    for (const file of files) {
      try {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: { status: 'uploading', progress: 50 }
        }));

        const formData = new FormData();
        formData.append('file', file);
        formData.append('startup_type', 'SaaS');

        const response = await fetch(`${API_BASE_URL}/api/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const result = await response.json();
        
        // Store in sessionStorage
        const analysisKey = `analysis_${result.analysis_id}`;
        const analysisData = {
          ...result,
          filename: file.name,
          timestamp: new Date().toISOString()
        };
        sessionStorage.setItem(analysisKey, JSON.stringify(analysisData));

        setUploadProgress(prev => ({
          ...prev,
          [file.name]: { status: 'completed', progress: 100 }
        }));

      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: { status: 'failed', progress: 0 }
        }));
      }
    }

    // Reload documents
    setTimeout(() => {
      loadRecentAnalyses();
      setUploading(false);
      setUploadProgress({});
    }, 1000);
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 mb-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Document Comparison</h1>
            <p className="text-blue-100">Compare multiple term sheets side-by-side to find the best deal</p>
          </div>
          <Scale className="w-16 h-16 opacity-50" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Document Selection Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-blue-600" />
              Select Documents
            </h2>
            
            <input
              type="text"
              placeholder="Comparison name (optional)"
              value={comparisonName}
              onChange={(e) => setComparisonName(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            {/* Batch Upload Section */}
            <div className="mb-4">
              <label className="block w-full">
                <div className="border-2 border-dashed border-blue-300 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all">
                  <Upload className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-700">
                    Upload Multiple Documents
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Select 2 or more PDFs/DOCX files
                  </p>
                </div>
                <input
                  type="file"
                  multiple
                  accept=".pdf,.docx"
                  onChange={handleMultipleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            </div>

            {/* Upload Progress */}
            {uploading && Object.keys(uploadProgress).length > 0 && (
              <div className="mb-4 space-y-2 max-h-40 overflow-y-auto">
                {Object.entries(uploadProgress).map(([filename, status]) => (
                  <div key={filename} className="bg-gray-50 rounded p-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="truncate flex-1 mr-2">{filename}</span>
                      <span className={`font-semibold ${
                        status.status === 'completed' ? 'text-green-600' :
                        status.status === 'failed' ? 'text-red-600' :
                        'text-blue-600'
                      }`}>
                        {status.status === 'completed' ? '✓' :
                         status.status === 'failed' ? '✗' :
                         '...'}
                      </span>
                    </div>
                    {status.status === 'uploading' && (
                      <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                        <div 
                          className="bg-blue-600 h-1 rounded-full transition-all"
                          style={{ width: `${status.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="space-y-2 mb-6 max-h-96 overflow-y-auto">
              {documents.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-gray-500 text-sm">
                    No documents yet. Upload multiple documents above.
                  </p>
                </div>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => toggleDocument(doc.id)}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedDocs.includes(doc.id)
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">{doc.filename}</p>
                        <p className={`text-xs font-semibold mt-1 ${getRiskColor(doc.riskScore)}`}>
                          Risk: {doc.riskScore}/100
                        </p>
                      </div>
                      {selectedDocs.includes(doc.id) && (
                        <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 ml-2" />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            <button
              onClick={handleCompare}
              disabled={selectedDocs.length < 2 || loading}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-semibold"
            >
              {loading ? 'Comparing...' : `Compare ${selectedDocs.length} Documents`}
            </button>
            
            {selectedDocs.length === 1 && (
              <p className="text-xs text-gray-500 mt-2 text-center">
                Select at least one more document
              </p>
            )}
          </div>
        </div>

        {/* Comparison Results */}
        <div className="lg:col-span-2">
          {comparisonResult ? (
            <div className="space-y-6">
              {/* Winner Card */}
              <div className="bg-gradient-to-br from-purple-600 via-purple-500 to-pink-500 rounded-xl p-8 text-white shadow-2xl">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <Trophy className="w-8 h-8 mr-3" />
                      <h2 className="text-3xl font-bold">Best Agreement</h2>
                    </div>
                    <p className="text-2xl font-bold mb-2">
                      {comparisonResult.documents?.find(d => d.document_id === comparisonResult.winner?.winner_document_id)?.filename?.replace(/^\d{8}_\d{6}_/, '') || 'Document 1'}
                    </p>
                    <p className="text-purple-100 text-lg">
                      ✨ Lowest overall risk - Best terms for your startup
                    </p>
                  </div>
                  <div className="text-right border-l-2 border-purple-300 pl-8 ml-8">
                    <p className="text-sm text-purple-200 uppercase tracking-wide">Risk Score</p>
                    <p className="text-5xl font-bold mb-2">
                      {comparisonResult.documents?.find(d => d.document_id === comparisonResult.winner?.winner_document_id)?.overall_risk_score || 0}/100
                    </p>
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <p className="text-xs text-purple-200">
                        {((comparisonResult.winner?.confidence || 0) * 100).toFixed(0)}% confidence in winner
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Document Comparison Table */}
              <div className="glass-card">
                <h3 className="text-xl font-bold mb-4 text-white">Side-by-Side Comparison</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-purple-500/30">
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">Document</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-300">Risk Score</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-300">Risk Level</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-300">Total Clauses</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-300">High Risk</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-300">Critical Risk</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparisonResult.documents?.map((doc, idx) => (
                        <tr 
                          key={doc.document_id} 
                          className={`border-b border-white/10 ${
                            doc.document_id === comparisonResult.winner?.winner_document_id 
                              ? 'bg-purple-500/20 font-semibold' 
                              : 'hover:bg-white/5'
                          }`}
                        >
                          <td className="py-3 px-4">
                            <div className="flex items-center">
                              {doc.document_id === comparisonResult.winner?.winner_document_id && (
                                <Trophy className="w-4 h-4 text-purple-400 mr-2" />
                              )}
                              <span className="truncate max-w-xs text-white" title={doc.filename}>
                                {doc.filename?.replace(/^\d{8}_\d{6}_/, '') || doc.filename}
                              </span>
                            </div>
                          </td>
                          <td className="text-center py-3 px-4">
                            <span className={`text-lg font-bold ${getRiskColor(doc.overall_risk_score)}`}>
                              {doc.overall_risk_score}/100
                            </span>
                          </td>
                          <td className="text-center py-3 px-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskBadge(doc.risk_level)}`}>
                              {doc.risk_level}
                            </span>
                          </td>
                          <td className="text-center py-3 px-4 text-gray-300">{doc.total_clauses}</td>
                          <td className="text-center py-3 px-4">
                            <span className="text-orange-400 font-semibold">{doc.high_risk_count}</span>
                          </td>
                          <td className="text-center py-3 px-4">
                            <span className="text-red-400 font-semibold">{doc.critical_risk_count}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Summary */}
              <div className="glass-card">
                <h3 className="text-xl font-bold mb-3 text-white flex items-center">
                  <span className="w-2 h-2 bg-purple-400 rounded-full mr-3"></span>
                  Comparison Summary
                </h3>
                <p className="text-gray-300 whitespace-pre-line leading-relaxed">{comparisonResult.summary}</p>
              </div>



              {/* Clause Comparison */}
              {comparisonResult.clause_comparison && Object.keys(comparisonResult.clause_comparison).length > 0 && (
                <div className="glass-card">
                  <h3 className="text-xl font-bold mb-4 text-white">📋 Clause-by-Clause Comparison</h3>
                  <div className="space-y-4">
                    {Object.entries(comparisonResult.clause_comparison).map(([clauseType, data]) => (
                      <div key={clauseType} className="border-b border-white/10 pb-4 last:border-0">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-semibold text-white text-lg">{clauseType}</h4>
                          <span className={`px-4 py-1 rounded-full text-xs font-semibold ${getRiskBadge(data.all_versions?.[0]?.risk_level || 'Low')}`}>
                            ✓ Best: Doc {data.winner_document || 1}
                          </span>
                        </div>
                        {data.all_versions && data.all_versions.length > 0 && (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {data.all_versions.map((version, idx) => (
                              <div key={idx} className={`rounded-lg p-3 border ${
                                version.document_id === data.winner_document
                                  ? 'bg-purple-500/20 border-purple-500/50'
                                  : 'bg-white/5 border-white/10'
                              }`}>
                                <div className="flex items-center justify-between mb-2">
                                  <p className="font-medium text-gray-300">Document {version.document_id}</p>
                                  {version.document_id === data.winner_document && (
                                    <span className="text-purple-400 text-xs">✓ Best</span>
                                  )}
                                </div>
                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getRiskBadge(version.risk_level)}`}>
                                  {version.risk_level}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Insights */}
              {comparisonResult.ai_insights && (
                <div className="glass-card border-2 border-purple-500/30">
                  <h3 className="text-xl font-bold mb-3 text-white flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2 text-purple-400" />
                    AI-Powered Insights
                  </h3>
                  <p className="text-gray-300 whitespace-pre-line leading-relaxed">{comparisonResult.ai_insights}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-lg p-12 text-center">
              <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                Select 2 or more documents and click Compare to see detailed analysis
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
