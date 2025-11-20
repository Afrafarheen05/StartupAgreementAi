import React, { useState } from "react";
import { Building2, TrendingUp, Leaf, Cloud, Heart, ShoppingCart, Cpu, Globe } from "lucide-react";

const STARTUP_TYPES = [
  { id: "fintech", name: "FinTech", icon: TrendingUp, color: "from-green-500 to-emerald-600" },
  { id: "healthtech", name: "HealthTech", icon: Heart, color: "from-red-500 to-pink-600" },
  { id: "agritech", name: "AgriTech", icon: Leaf, color: "from-lime-500 to-green-600" },
  { id: "saas", name: "SaaS", icon: Cloud, color: "from-blue-500 to-cyan-600" },
  { id: "ecommerce", name: "E-Commerce", icon: ShoppingCart, color: "from-purple-500 to-indigo-600" },
  { id: "ai", name: "AI/ML", icon: Cpu, color: "from-orange-500 to-amber-600" },
  { id: "other", name: "Other", icon: Globe, color: "from-gray-500 to-slate-600" },
];

const FUNDING_STAGES = [
  { 
    id: "pre-seed", 
    name: "Pre-Seed", 
    desc: "Early stage, typically $50K-$500K",
    risks: ["High equity dilution", "Loose term structures"]
  },
  { 
    id: "seed", 
    name: "Seed", 
    desc: "First institutional round, $500K-$2M",
    risks: ["Liquidation preferences", "Board control issues"]
  },
  { 
    id: "series-a", 
    name: "Series A", 
    desc: "Growth stage, $2M-$15M",
    risks: ["Anti-dilution clauses", "Investor veto rights"]
  },
  { 
    id: "series-b", 
    name: "Series B+", 
    desc: "Scale stage, $15M+",
    risks: ["Complex cap table", "Multiple stakeholder conflicts"]
  },
];

export default function StartupTypeSelector({ onComplete }) {
  const [selectedType, setSelectedType] = useState(null);
  const [selectedStage, setSelectedStage] = useState(null);
  const [step, setStep] = useState(1);

  const handleContinue = () => {
    if (step === 1 && selectedType) {
      setStep(2);
    } else if (step === 2 && selectedStage) {
      onComplete({ type: selectedType, stage: selectedStage });
    }
  };

  return (
    <div className="glass-card">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Step {step} of 2</span>
          <span className="text-sm text-gray-400">{step === 1 ? "Startup Type" : "Funding Stage"}</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(step / 2) * 100}%` }}
          />
        </div>
      </div>

      {step === 1 ? (
        <>
          <h2 className="text-2xl font-bold text-white mb-2">Select Your Startup Type</h2>
          <p className="text-gray-300 mb-6">
            This helps us provide industry-specific risk analysis tailored to your sector.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
            {STARTUP_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`
                    relative p-6 rounded-xl border-2 transition-all duration-200
                    ${selectedType === type.id
                      ? 'border-blue-500 bg-blue-500/10 scale-105'
                      : 'border-gray-600 hover:border-gray-500 bg-gray-800/30'
                    }
                  `}
                >
                  <div className={`
                    w-12 h-12 rounded-lg bg-gradient-to-br ${type.color} 
                    flex items-center justify-center mb-3 mx-auto
                  `}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <p className="text-white font-semibold text-center">{type.name}</p>
                  
                  {selectedType === type.id && (
                    <div className="absolute top-2 right-2 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">✓</span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </>
      ) : (
        <>
          <h2 className="text-2xl font-bold text-white mb-2">Select Funding Stage</h2>
          <p className="text-gray-300 mb-6">
            Different stages have different risk profiles and negotiation leverage.
          </p>

          <div className="space-y-4 mb-6">
            {FUNDING_STAGES.map((stage) => (
              <button
                key={stage.id}
                onClick={() => setSelectedStage(stage.id)}
                className={`
                  w-full p-5 rounded-xl border-2 text-left transition-all duration-200
                  ${selectedStage === stage.id
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-600 hover:border-gray-500 bg-gray-800/30'
                  }
                `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">{stage.name}</h3>
                    <p className="text-sm text-gray-400 mb-2">{stage.desc}</p>
                    <div className="flex flex-wrap gap-2">
                      {stage.risks.map((risk, idx) => (
                        <span 
                          key={idx}
                          className="text-xs px-2 py-1 rounded-full bg-red-500/20 text-red-300 border border-red-500/30"
                        >
                          {risk}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {selectedStage === stage.id && (
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center ml-4 flex-shrink-0">
                      <span className="text-white text-sm">✓</span>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-700">
        {step === 2 && (
          <button
            onClick={() => setStep(1)}
            className="px-6 py-2 text-gray-300 hover:text-white transition-colors"
          >
            ← Back
          </button>
        )}
        
        <button
          onClick={handleContinue}
          disabled={step === 1 ? !selectedType : !selectedStage}
          className={`
            ml-auto px-6 py-2 rounded-lg font-semibold transition-all
            ${(step === 1 ? selectedType : selectedStage)
              ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:shadow-lg hover:shadow-blue-500/50'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {step === 1 ? 'Continue' : 'Start Analysis'}
        </button>
      </div>
    </div>
  );
}
