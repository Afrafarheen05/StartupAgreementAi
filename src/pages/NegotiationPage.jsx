import React, { useState } from 'react';
import { MessageSquare, Trophy, Target, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { api } from '../utils/api';

export default function NegotiationPage() {
  const [session, setSession] = useState(null);
  const [proposal, setProposal] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [loading, setLoading] = useState(false);

  const startNegotiation = async (clause, profile = 'balanced') => {
    setLoading(true);
    try {
      // Check if backend is running
      const healthCheck = await fetch('http://localhost:8000/');
      if (!healthCheck.ok) {
        alert('⚠️ Backend server is not running!\n\nPlease start it:\n\n1. Open terminal\n2. cd backend\n3. python -m uvicorn app.main:app --reload');
        return;
      }
      
      const result = await api.startNegotiation(clause, profile, 'Series A', 'SaaS');
      setSession(result);
    } catch (error) {
      console.error('Failed to start negotiation:', error);
      alert(`Failed to start negotiation: ${error.message}\n\nMake sure the backend server is running.`);
    } finally {
      setLoading(false);
    }
  };

  const submitCounterOffer = async () => {
    if (!proposal.trim()) {
      alert('Please enter your counter-offer');
      return;
    }

    setLoading(true);
    try {
      const result = await api.makeCounterOffer(session.session_id, proposal, reasoning);
      setSession(result);
      setProposal('');
      setReasoning('');
    } catch (error) {
      console.error('Counter-offer failed:', error);
      alert('Failed to submit counter-offer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-8 mb-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Negotiation Simulator</h1>
        <p className="text-purple-100">Practice negotiating with AI investors before the real thing</p>
      </div>

      {!session ? (
        /* Setup Screen */
        <div className="glass-card">
          <h2 className="text-2xl font-semibold mb-6 text-white">Start Negotiation Training</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <InvestorProfileCard
              title="Founder-Friendly"
              description="Flexible, values partnership. Willing to negotiate and find win-win solutions."
              difficulty="Easy"
              color="green"
              tactics="• Partnership focus • Flexible terms • Founder success oriented"
              onClick={() => startNegotiation(getExampleClause(), 'founder_friendly')}
            />
            <InvestorProfileCard
              title="Balanced"
              description="Fair but firm negotiator. Uses market benchmarks and data-driven approach."
              difficulty="Medium"
              color="blue"
              tactics="• Market benchmarks • Data-driven • Willing to compromise"
              onClick={() => startNegotiation(getExampleClause(), 'balanced')}
            />
            <InvestorProfileCard
              title="Aggressive"
              description="Pushes hard on terms. Uses pressure tactics and rarely compromises."
              difficulty="Hard"
              color="red"
              tactics="• Time pressure • Non-negotiable • Industry standards focus"
              onClick={() => startNegotiation(getExampleClause(), 'aggressive')}
            />
          </div>

          <div className="bg-purple-500/20 border-l-4 border-purple-500 p-4 rounded">
            <h3 className="font-semibold text-white mb-2">💡 How It Works</h3>
            <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
              <li>Choose an investor profile to practice with - each has unique negotiation style</li>
              <li>Review the investor's opening position</li>
              <li>Make counter-offers with your reasoning</li>
              <li>Receive AI-powered feedback on your moves</li>
              <li>Learn negotiation strategies that work</li>
            </ul>
          </div>
        </div>
      ) : (
        /* Active Negotiation */
        <div className="space-y-6">
          {/* Status Header */}
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold text-white">
                  Negotiating: {session.clause.type || session.clause.clause_type || 'Unknown Clause'}
                </h2>
                <p className="text-sm text-gray-300">
                  Investor: {session.investor_profile.replace('_', ' ')} | Round {session.current_round}/{session.max_rounds}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400">Success Probability</div>
                <div className="text-3xl font-bold text-purple-300">
                  {(session.success_probability * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {session.status === 'completed' && (
              <div className={`p-4 rounded-lg border-l-4 ${
                session.outcome === 'accepted' ? 'bg-green-500/20 border-green-400' :
                session.outcome === 'rejected' ? 'bg-red-500/20 border-red-400' :
                'bg-yellow-500/20 border-yellow-400'
              }`}>
                <div className="flex items-center">
                  {session.outcome === 'accepted' ? <CheckCircle className="w-6 h-6 text-green-300 mr-2" /> :
                   <AlertTriangle className="w-6 h-6 text-red-300 mr-2" />}
                  <div>
                    <div className="font-semibold text-white">
                      {session.outcome === 'accepted' ? 'Success!' : 'Deal Fell Through'}
                    </div>
                    <div className="text-sm text-gray-300">
                      Final Score: {session.final_score}/100
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Negotiation History */}
          <div className="glass-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4 text-white">Negotiation Thread</h3>
            <div className="space-y-4">
              {session.history.map((move, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg ${
                    move.actor === 'founder' ? 'bg-blue-500/20 ml-8 border border-blue-400/30' : 'bg-white/5 mr-8 border border-white/10'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-semibold text-white">
                      {move.actor === 'founder' ? '👤 You' : '💼 Investor'}
                    </div>
                    <div className="text-xs text-gray-400">Round {move.round}</div>
                  </div>
                  <p className="text-gray-200 mb-2">{move.proposal}</p>
                  
                  {move.analysis && (
                    <div className="mt-3 pt-3 border-t border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-300">Move Quality:</span>
                        <span className={`font-bold ${
                          move.analysis.move_quality_score >= 70 ? 'text-green-300' :
                          move.analysis.move_quality_score >= 50 ? 'text-yellow-300' :
                          'text-red-300'
                        }`}>
                          {move.analysis.move_quality_score}/100
                        </span>
                      </div>
                      {move.analysis.tips && move.analysis.tips.length > 0 && (
                        <div className="text-xs text-gray-400 italic">
                          💡 {move.analysis.tips[0]}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Counter-Offer Form */}
          {session.status === 'in_progress' && (
            <div className="glass-card rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-white">Your Counter-Offer</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Your Proposal *
                  </label>
                  <textarea
                    value={proposal}
                    onChange={(e) => setProposal(e.target.value)}
                    className="w-full bg-white/10 border border-white/20 text-white rounded-lg p-3 focus:ring-2 focus:ring-purple-400 focus:border-transparent placeholder-gray-400"
                    rows="4"
                    placeholder="State your counter-offer clearly and professionally..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Your Reasoning (optional but recommended)
                  </label>
                  <textarea
                    value={reasoning}
                    onChange={(e) => setReasoning(e.target.value)}
                    className="w-full bg-white/10 border border-white/20 text-white rounded-lg p-3 focus:ring-2 focus:ring-purple-400 focus:border-transparent placeholder-gray-400"
                    rows="3"
                    placeholder="Explain why your counter-offer is fair (use data, market benchmarks, etc.)..."
                  />
                </div>

                <button
                  onClick={submitCounterOffer}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:from-gray-600 disabled:to-gray-600 font-semibold transition-all"
                >
                  {loading ? 'Submitting...' : 'Submit Counter-Offer'}
                </button>
              </div>
            </div>
          )}

          {/* Lessons Learned */}
          {session.lessons && session.lessons.length > 0 && (
            <div className="glass-card rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center text-white">
                <Trophy className="w-5 h-5 mr-2 text-purple-300" />
                Lessons Learned
              </h3>
              <div className="space-y-3">
                {session.lessons.map((lesson, idx) => (
                  <div key={idx} className="bg-white/10 p-4 rounded-lg border border-white/10">
                    <div className="font-semibold text-white mb-1">{lesson.lesson}</div>
                    <div className="text-sm text-gray-300">{lesson.details}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function InvestorProfileCard({ title, description, difficulty, color, tactics, onClick }) {
  const colors = {
    green: 'border-green-500/50 bg-green-500/10 hover:bg-green-500/20',
    blue: 'border-blue-500/50 bg-blue-500/10 hover:bg-blue-500/20',
    red: 'border-red-500/50 bg-red-500/10 hover:bg-red-500/20'
  };

  const badgeColors = {
    green: 'bg-green-500/30 text-green-200',
    blue: 'bg-blue-500/30 text-blue-200',
    red: 'bg-red-500/30 text-red-200'
  };

  return (
    <div
      onClick={onClick}
      className={`cursor-pointer border-2 ${colors[color]} rounded-lg p-6 transition-all hover:shadow-xl hover:scale-105`}
    >
      <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
      <p className="text-sm text-gray-300 mb-3 h-12">{description}</p>
      {tactics && (
        <div className="mb-3 text-xs text-gray-400 whitespace-pre-line border-t border-white/10 pt-3">
          {tactics}
        </div>
      )}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-400">Difficulty</span>
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${badgeColors[color]}`}>
          {difficulty}
        </span>
      </div>
    </div>
  );
}

function getExampleClause() {
  return {
    type: 'Liquidation Preference',
    text: 'In the event of any liquidation or winding up of the Company, the holders of Series A Preferred Stock shall be entitled to receive, prior to any distribution to holders of Common Stock, an amount equal to 2x the original purchase price plus any declared but unpaid dividends (the "Liquidation Preference").',
    risk_level: 'High',
    confidence: 0.75
  };
}
