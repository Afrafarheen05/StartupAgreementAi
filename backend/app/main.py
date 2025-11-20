"""
FastAPI Main Application - No Database Version
All processing happens in real-time, results returned directly
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from typing import Dict, Optional
from datetime import datetime

from app.ml.analysis_engine import AnalysisEngine
from app.ml.chat_assistant import ChatAssistant

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

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs('./trained_models', exist_ok=True)

# Initialize ML engine
print("Initializing ML Analysis Engine...")
analysis_engine = AnalysisEngine(MODEL_PATH)
chat_assistant = ChatAssistant()
print("✅ Analysis Engine Ready!")

# In-memory storage for recent analyses (for chat context)
recent_analyses: Dict[str, Dict] = {}


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


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting AgreemShield AI Backend")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
