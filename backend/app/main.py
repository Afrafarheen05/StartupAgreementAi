"""
FastAPI Main Application - No Database Version
All processing happens in real-time, results returned directly
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import json
from typing import Dict, Optional
from datetime import datetime

from app.ml.analysis_engine import AnalysisEngine
from app.ml.chat_assistant import ChatAssistant
from app.ml.comparison_engine import ComparisonEngine
from app.ml.negotiation_simulator import NegotiationSimulator
from app.ml.compliance_checker import ComplianceChecker
from app.ml.version_control import VersionControl
from app.ml.benchmark_engine import BenchmarkEngine
from app.ml.contract_generator import ContractGenerator

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AgreemShield AI API",
    description="ML-powered startup agreement risk analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
MODEL_PATH = os.getenv('MODEL_PATH', './trained_models/risk_classifier.pkl')
PERSISTENCE_DIR = './persistence'

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs('./trained_models', exist_ok=True)
os.makedirs(PERSISTENCE_DIR, exist_ok=True)

# Persistence file
ANALYSES_FILE = os.path.join(PERSISTENCE_DIR, 'recent_analyses.json')

# Initialize all ML engines
print("Initializing AI Engines...")
analysis_engine = AnalysisEngine(MODEL_PATH)
chat_assistant = ChatAssistant()
comparison_engine = ComparisonEngine()
negotiation_simulator = NegotiationSimulator()
compliance_checker = ComplianceChecker()
version_control = VersionControl()
benchmark_engine = BenchmarkEngine()
contract_generator = ContractGenerator()
print("✅ All AI Engines Ready!")

# In-memory storage
recent_analyses: Dict[str, Dict] = {}
negotiation_sessions: Dict[str, Dict] = {}


def save_analyses_to_disk():
    """Save recent analyses to disk for persistence"""
    try:
        with open(ANALYSES_FILE, 'w') as f:
            json.dump(recent_analyses, f)
        print(f"💾 Saved {len(recent_analyses)} analyses to disk")
    except Exception as e:
        print(f"⚠️  Failed to save analyses: {e}")


def load_analyses_from_disk():
    """Load recent analyses from disk on startup"""
    global recent_analyses
    try:
        if os.path.exists(ANALYSES_FILE):
            with open(ANALYSES_FILE, 'r') as f:
                recent_analyses = json.load(f)
            print(f"✅ Loaded {len(recent_analyses)} analyses from disk")
            print(f"   Available IDs: {list(recent_analyses.keys())}")
        else:
            print("ℹ️  No saved analyses found")
    except Exception as e:
        print(f"⚠️  Failed to load analyses: {e}")
        recent_analyses = {}


# Load analyses on startup
load_analyses_from_disk()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AgreemShield AI",
        "version": "1.0.0",
        "ml_engine": "ready"
    }


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    startup_type: str = Form("SaaS")
):
    """
    Upload and analyze a document - Returns complete analysis directly
    No database storage, pure real-time processing
    """
    try:
        print(f"\n📄 Received file: {file.filename}")
        print(f"📊 Startup type: {startup_type}")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        print(f"💾 Saving to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze document with ML/NLP
        print(f"🔍 Starting ML analysis...")
        result = analysis_engine.analyze_document(file_path, startup_type)
        
        if not result['success']:
            # Clean up file if analysis failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        # Generate unique ID for this analysis
        analysis_id = timestamp
        result['analysis_id'] = analysis_id
        result['filename'] = file.filename
        
        # Store in memory for chat context
        recent_analyses[analysis_id] = result
        
        # Save to disk for persistence
        save_analyses_to_disk()
        
        print(f"✅ Analysis complete!")
        print(f"   - Clauses found: {len(result['clauses'])}")
        print(f"   - Risk score: {result['risk_assessment']['overall_score']}")
        print(f"   - Risk level: {result['risk_assessment']['overall_level']}\n")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID from memory"""
    if analysis_id not in recent_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found or expired")
    
    return JSONResponse(content=recent_analyses[analysis_id])


@app.post("/api/train")
async def train_model():
    """Train the risk classification model from labeled data"""
    try:
        print("\n🚀 Starting model training...")
        
        # Path to training data
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'labeled_clauses.csv')
        
        if not os.path.exists(csv_path):
            # Try alternative path
            csv_path = '../labeled_clauses.csv'
            if not os.path.exists(csv_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Training data not found. Place labeled_clauses.csv in project root."
                )
        
        print(f"📂 Training data: {csv_path}")
        
        # Train model
        result = analysis_engine.train_model(csv_path)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        print(f"✅ Training complete!")
        print(f"   - Accuracy: {result.get('metrics', {}).get('accuracy', 0)*100:.1f}%")
        print(f"   - Samples: {result.get('metrics', {}).get('training_samples', 0)}\n")
        
        return {
            'success': True,
            'message': 'Model trained successfully',
            'metrics': result.get('metrics', {}),
            'model_path': result.get('model_path')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.post("/api/chat")
async def chat_with_ai(message: dict):
    """
    Chat interface for asking questions about clauses and risks
    Uses intelligent NLP-based AI assistant
    """
    try:
        user_message = message.get('message', '')
        analysis_id = message.get('analysis_id')
        
        # Get context if analysis_id provided
        context = None
        if analysis_id and analysis_id in recent_analyses:
            analysis = recent_analyses[analysis_id]
            context = {
                'clauses': analysis['clauses'],
                'risk_assessment': analysis['risk_assessment'],
                'recommendations': analysis.get('recommendations', []),
                'risk_level': analysis['risk_assessment']['overall_level'],
                'overall_score': analysis['risk_assessment']['overall_score'],
                'dangerous_clauses': analysis['risk_assessment'].get('dangerous_clauses', []),
                'clause_count': analysis['risk_assessment']['clause_count'],
                'risk_categories': analysis['risk_assessment'].get('risk_categories', {})
            }
        
        # Generate intelligent response using ChatAssistant
        response = chat_assistant.get_response(user_message, context)
        
        return {
            'reply': response,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


def _generate_chat_response(message: str, context: Optional[dict]) -> str:
    """Generate chat response based on user message and context"""
    
    # Pattern-based responses
    if any(word in message for word in ['liquidation', 'preference']):
        if context and any(c['type'] == 'Liquidation Preference' for c in context['clauses']):
            clause = next(c for c in context['clauses'] if c['type'] == 'Liquidation Preference')
            return f"Your agreement has a Liquidation Preference clause with {clause['risk_level']} risk. {clause.get('explanation', 'This affects how proceeds are distributed in an exit.')}"
        return "Liquidation preference determines the order investors get paid in an acquisition. 1x non-participating is most founder-friendly."
    
    elif any(word in message for word in ['anti-dilution', 'dilution']):
        if context and any(c['type'] == 'Anti-Dilution' for c in context['clauses']):
            clause = next(c for c in context['clauses'] if c['type'] == 'Anti-Dilution')
            return f"Your agreement includes Anti-Dilution provisions ({clause['risk_level']} risk). {clause.get('explanation', 'This protects investors if you raise money at a lower valuation.')}"
        return "Anti-dilution clauses protect investors from dilution in down rounds. Weighted average is standard; full ratchet is harsh."
    
    elif any(word in message for word in ['board', 'control']):
        if context and any(c['type'] == 'Board Control' for c in context['clauses']):
            clause = next(c for c in context['clauses'] if c['type'] == 'Board Control')
            return f"Board composition: {clause['risk_level']} risk. {clause.get('explanation', 'This determines who makes key decisions.')}"
        return "Board control determines who makes strategic decisions. Balanced boards (2 founders, 1 investor, 2 independent) work best."
    
    elif any(word in message for word in ['risk', 'score', 'overall']):
        if context:
            risk = context['risk_assessment']
            return f"Overall risk score: {risk['overall_score']}/100 ({risk['overall_level']} risk). Found {risk['red_flags']} critical clauses. {risk['summary']}"
        return "I can analyze your agreement's overall risk level. Upload a document to get started."
    
    elif any(word in message for word in ['recommend', 'negotiate', 'fix']):
        if context and context.get('recommendations'):
            top_rec = context['recommendations'][0]
            return f"Top priority: {top_rec['clause']} - {top_rec['recommendation']} Impact: {top_rec['expected_impact']}"
        return "I provide negotiation recommendations for risky clauses. Upload your agreement to get specific advice."
    
    elif any(word in message for word in ['future', 'predict', 'what if']):
        if context:
            preds = context.get('predictions', [])
            if preds:
                pred = preds[0]
                return f"{pred['timeframe']}: {pred['description']} (Probability: {pred['probability']*100:.0f}%)"
        return "I can predict future risks based on your current agreement terms. Upload a document for timeline predictions."
    
    else:
        return "I can help you understand your startup agreement! Ask me about specific clauses, overall risk, negotiation strategies, or future predictions. Upload a document for detailed analysis."


@app.get("/api/stats")
async def get_statistics():
    """Get basic statistics from memory"""
    total = len(recent_analyses)
    
    if total == 0:
        return {
            'total_analyses': 0,
            'message': 'No analyses yet. Upload a document to get started!'
        }
    
    analyses = list(recent_analyses.values())
    avg_risk = sum(a['risk_assessment']['overall_score'] for a in analyses) / total
    high_risk = sum(1 for a in analyses if a['risk_assessment']['overall_level'] == 'High')
    
    return {
        'total_analyses': total,
        'avg_risk_score': round(avg_risk, 1),
        'high_risk_count': high_risk
    }


# ==================== COMPARISON ENGINE ENDPOINTS ====================
@app.post("/api/compare")
async def compare_documents(comparison_request: dict):
    """
    Compare multiple documents side-by-side
    
    Body: {
        "analysis_ids": ["id1", "id2", "id3"],
        "comparison_name": "Investor Comparison"
    }
    """
    try:
        analysis_ids = comparison_request.get('analysis_ids', [])
        comparison_name = comparison_request.get('comparison_name', 'Document Comparison')
        
        if len(analysis_ids) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 documents to compare")
        
        # Debug: Show what's in memory
        print(f"\n🔍 Comparison request for: {analysis_ids}")
        print(f"📊 Available analyses in memory: {list(recent_analyses.keys())}")
        
        # Get documents from memory
        documents = []
        missing_ids = []
        for aid in analysis_ids:
            if aid not in recent_analyses:
                missing_ids.append(aid)
            else:
                documents.append(recent_analyses[aid])
        
        if missing_ids:
            raise HTTPException(
                status_code=404, 
                detail=f"Analyses not found: {', '.join(missing_ids)}. Available IDs: {', '.join(list(recent_analyses.keys())[:5])}"
            )
        
        # Perform comparison
        result = comparison_engine.compare_documents(documents, comparison_name)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# ==================== NEGOTIATION SIMULATOR ENDPOINTS ====================
@app.post("/api/negotiation/start")
async def start_negotiation(request: dict):
    """
    Start a negotiation simulation
    
    Body: {
        "clause": {...},
        "investor_profile": "balanced",
        "funding_stage": "Series A",
        "startup_type": "SaaS"
    }
    """
    try:
        clause = request.get('clause')
        investor_profile = request.get('investor_profile', 'balanced')
        funding_stage = request.get('funding_stage', 'Series A')
        startup_type = request.get('startup_type', 'SaaS')
        
        if not clause:
            raise HTTPException(status_code=400, detail="Clause is required")
        
        session = negotiation_simulator.start_negotiation(
            clause, investor_profile, funding_stage, startup_type
        )
        
        # Store session
        negotiation_sessions[session['session_id']] = session
        
        return JSONResponse(content=session)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start negotiation: {str(e)}")


@app.post("/api/negotiation/{session_id}/counter")
async def make_counter_offer(session_id: str, request: dict):
    """
    Make a counter-offer in negotiation
    
    Body: {
        "proposal": "Your counter-offer text",
        "reasoning": "Your reasoning"
    }
    """
    try:
        if session_id not in negotiation_sessions:
            raise HTTPException(status_code=404, detail="Negotiation session not found")
        
        proposal = request.get('proposal', '')
        reasoning = request.get('reasoning', '')
        
        if not proposal:
            raise HTTPException(status_code=400, detail="Proposal is required")
        
        session = negotiation_sessions[session_id]
        updated_session = negotiation_simulator.make_counter_offer(
            session, proposal, reasoning
        )
        
        negotiation_sessions[session_id] = updated_session
        
        return JSONResponse(content=updated_session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Counter-offer failed: {str(e)}")


@app.get("/api/negotiation/{session_id}")
async def get_negotiation_session(session_id: str):
    """Get negotiation session details"""
    if session_id not in negotiation_sessions:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    
    return JSONResponse(content=negotiation_sessions[session_id])


# ==================== COMPLIANCE CHECKER ENDPOINTS ====================
@app.post("/api/compliance/check")
async def check_compliance(request: dict):
    """
    Check document compliance across jurisdictions
    
    Body: {
        "analysis_id": "...",
        "jurisdictions": ["US", "EU", "UK"]
    }
    """
    try:
        analysis_id = request.get('analysis_id')
        jurisdictions = request.get('jurisdictions', ['US'])
        
        if not analysis_id or analysis_id not in recent_analyses:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = recent_analyses[analysis_id]
        document_text = " ".join([c['clause_text'] for c in analysis['clauses']])
        
        result = compliance_checker.check_compliance(
            document_text,
            analysis['clauses'],
            jurisdictions
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")


@app.get("/api/compliance/requirements/{jurisdiction}")
async def get_jurisdiction_requirements(jurisdiction: str):
    """Get compliance requirements for a jurisdiction"""
    result = compliance_checker.get_jurisdiction_requirements(jurisdiction)
    return JSONResponse(content=result)


# ==================== VERSION CONTROL ENDPOINTS ====================
@app.post("/api/version/create")
async def create_version(request: dict):
    """
    Create a new document version
    
    Body: {
        "document_id": "...",
        "analysis_id": "...",
        "created_by": "user@example.com",
        "change_summary": "Updated liquidation preference"
    }
    """
    try:
        document_id = request.get('document_id')
        analysis_id = request.get('analysis_id')
        created_by = request.get('created_by', 'Anonymous')
        change_summary = request.get('change_summary', '')
        
        if not analysis_id or analysis_id not in recent_analyses:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = recent_analyses[analysis_id]
        content = " ".join([c['clause_text'] for c in analysis['clauses']])
        
        version = version_control.create_version(
            document_id,
            content,
            analysis['clauses'],
            created_by,
            change_summary
        )
        
        return JSONResponse(content=version)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version creation failed: {str(e)}")


@app.get("/api/version/history/{document_id}")
async def get_version_history(document_id: str):
    """Get version history for a document"""
    history = version_control.get_version_history(document_id)
    return JSONResponse(content={'document_id': document_id, 'versions': history})


@app.post("/api/version/compare")
async def compare_versions(request: dict):
    """
    Compare two document versions
    
    Body: {
        "document_id": "...",
        "version_a": 1,
        "version_b": 2
    }
    """
    try:
        document_id = request.get('document_id')
        version_a = request.get('version_a')
        version_b = request.get('version_b')
        
        result = version_control.compare_versions(document_id, version_a, version_b)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version comparison failed: {str(e)}")


# ==================== BENCHMARK ENGINE ENDPOINTS ====================
@app.post("/api/benchmark/document")
async def benchmark_document(request: dict):
    """
    Benchmark entire document against market
    
    Body: {
        "analysis_id": "...",
        "startup_type": "SaaS",
        "funding_stage": "Series A"
    }
    """
    try:
        analysis_id = request.get('analysis_id')
        startup_type = request.get('startup_type', 'SaaS')
        funding_stage = request.get('funding_stage', 'Series A')
        
        if not analysis_id or analysis_id not in recent_analyses:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = recent_analyses[analysis_id]
        
        result = benchmark_engine.benchmark_document(
            analysis['clauses'],
            startup_type,
            funding_stage
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmarking failed: {str(e)}")


@app.get("/api/benchmark/trends")
async def get_industry_trends(startup_type: str = "SaaS", funding_stage: str = "Series A"):
    """Get industry trends and standards"""
    result = benchmark_engine.get_industry_trends(startup_type, funding_stage)
    return JSONResponse(content=result)


# ==================== CONTRACT GENERATION ENDPOINTS ====================
@app.post("/api/generate/alternative")
async def generate_alternative_clause(request: dict):
    """
    Generate founder-friendly alternative to a clause
    
    Body: {
        "clause": {...},
        "startup_type": "SaaS",
        "funding_stage": "Series A"
    }
    """
    try:
        clause = request.get('clause')
        startup_type = request.get('startup_type', 'SaaS')
        funding_stage = request.get('funding_stage', 'Series A')
        
        if not clause:
            raise HTTPException(status_code=400, detail="Clause is required")
        
        result = contract_generator.generate_founder_friendly_alternative(
            clause, startup_type, funding_stage
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/api/generate/document")
async def generate_custom_agreement(request: dict):
    """
    Generate custom agreement from template
    
    Body: {
        "template_name": "SAFE",
        "parameters": {
            "amount": 500000,
            "valuation_cap": 10000000,
            ...
        },
        "customizations": {...}
    }
    """
    try:
        template_name = request.get('template_name')
        parameters = request.get('parameters', {})
        customizations = request.get('customizations')
        
        if not template_name:
            raise HTTPException(status_code=400, detail="Template name is required")
        
        result = contract_generator.generate_custom_agreement(
            template_name, parameters, customizations
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")


@app.get("/api/generate/templates")
async def list_templates():
    """List available agreement templates"""
    return JSONResponse(content={'templates': contract_generator.TEMPLATES})


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting AgreemShield AI Backend with All Features")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
