# AgreemShield AI - Backend

ML/NLP-powered startup agreement risk analysis backend built with FastAPI.

## Features

- **Document Processing**: PDF and DOCX extraction with OCR fallback
- **Clause Extraction**: NLP-based identification of 15+ clause types
- **Risk Classification**: ML model trained on labeled data
- **Future Predictions**: Timeline-based risk predictions (6mo to 3+ years)
- **Smart Recommendations**: Actionable negotiation strategies
- **RESTful API**: Complete FastAPI endpoints for frontend integration

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **ML**: scikit-learn (RandomForest), sentence-transformers
- **NLP**: spaCy, transformers (BERT)
- **Document Processing**: PyPDF2, python-docx, pytesseract (OCR)
- **Database**: SQLite + SQLAlchemy
- **Storage**: Local file system for uploads and trained models

## Quick Start

### 1. Setup Environment

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# OR run setup script (does everything)
python setup.py
```

### 2. Train the Model

```bash
# Ensure labeled_clauses.csv is in project root
python train_model.py
```

Expected output:
```
Training model...
✅ Training completed successfully!
   Accuracy: 85.3%
   Training samples: 158
```

### 3. Start the Server

```bash
# Method 1: Direct
python -m app.main

# Method 2: With Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/

# Upload and analyze document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@agreement.pdf" \
  -F "startup_type=SaaS"
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── ml/                        # ML/NLP modules
│   │   ├── document_processor.py  # PDF/DOCX extraction
│   │   ├── clause_extractor.py    # Clause identification
│   │   ├── risk_classifier.py     # ML risk classification
│   │   ├── future_predictor.py    # Risk predictions
│   │   ├── recommendation_engine.py # Negotiation recommendations
│   │   └── analysis_engine.py     # Main orchestrator
│   └── models/
│       └── database.py            # SQLAlchemy models
├── uploads/                       # Uploaded documents
├── trained_models/                # Saved ML models
├── requirements.txt               # Python dependencies
├── .env                          # Configuration
├── train_model.py                # Training script
└── setup.py                      # Setup script
```

## API Endpoints

### POST /api/upload
Upload and analyze a document

**Request:**
- `file`: PDF or DOCX file
- `startup_type`: One of: SaaS, FinTech, HealthTech, AgriTech

**Response:**
```json
{
  "success": true,
  "analysis_id": 123,
  "clauses": [...],
  "risk_assessment": {...},
  "future_predictions": [...],
  "recommendations": [...]
}
```

### GET /api/analysis/{id}
Get analysis results by ID

### GET /api/analyses
List recent analyses

### GET /api/clause/{clause_id}
Get detailed clause information (format: `analysis_id:clause_index`)

### POST /api/chat
Chat with AI about clauses and risks

**Request:**
```json
{
  "message": "Explain liquidation preference",
  "analysis_id": 123
}
```

### POST /api/train
Train the model from labeled data

### GET /api/stats
Get platform statistics

## ML Pipeline

### 1. Document Processing
- Extract text from PDF (PyPDF2)
- Extract text from DOCX (python-docx)
- OCR fallback for scanned PDFs (pytesseract)
- Text cleaning and normalization
- Section splitting

### 2. Clause Extraction
- Keyword-based matching
- Regex pattern recognition
- spaCy NER (Named Entity Recognition)
- Context analysis
- 15+ clause types identified

### 3. Risk Classification
- TF-IDF feature extraction
- RandomForest classifier
- Rule-based risk patterns
- Context-aware adjustments
- 3-tier risk levels (High, Medium, Low)

### 4. Future Prediction
- Timeline-based predictions
- Probability calculations
- Impact assessments
- 4 time periods: 6-12mo, 1-2yr, 2-3yr, 3+yr

### 5. Recommendations
- Priority-based ranking
- Negotiation strategies
- Expected impact estimation
- Industry benchmarks

## Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///./agreemshield.db

# File uploads
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# ML Models
MODEL_PATH=./trained_models/risk_classifier.pkl
SPACY_MODEL=en_core_web_sm

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Training Data Format

`labeled_clauses.csv` should have these columns:

```csv
clause_text,clause_type,risk_level
"Investor receives 3x participating liquidation preference...",Liquidation Preference,High
"Weighted average anti-dilution protection...",Anti-Dilution,Medium
```

**Required columns:**
- `clause_text`: The clause text
- `clause_type`: One of 15 supported types
- `risk_level`: High, Medium, or Low

**Supported clause types:**
- Liquidation Preference
- Anti-Dilution
- Board Control
- Vesting
- IP Assignment
- Drag-Along Rights
- Information Rights
- No-Shop Clause
- Pro-Rata Rights
- Pay-to-Play
- Conversion Rights
- Redemption Rights
- Representations & Warranties
- Voting Rights
- Exit Rights

## Development

### Adding New Clause Types

1. Update `clause_extractor.py`:
```python
self.clause_patterns['New Clause Type'] = {
    'keywords': ['keyword1', 'keyword2'],
    'patterns': [r'regex pattern']
}
```

2. Update `recommendation_engine.py`:
```python
self.recommendations_db['New Clause Type'] = {
    'High': {...},
    'Medium': {...}
}
```

3. Retrain model with new labeled data

### Testing

```bash
# Test document processing
python -c "from app.ml.document_processor import DocumentProcessor; dp = DocumentProcessor(); print(dp.process_document('test.pdf'))"

# Test clause extraction
python -c "from app.ml.clause_extractor import ClauseExtractor; ce = ClauseExtractor(); print(ce.extract_clauses('sample text'))"

# Test risk classification
python -c "from app.ml.risk_classifier import RiskClassifier; rc = RiskClassifier(); print(rc.classify_risk('sample clause', 'Liquidation Preference'))"
```

## Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# Production
export DATABASE_URL=postgresql://user:pass@host/db
export UPLOAD_DIR=/var/lib/agreemshield/uploads
export MODEL_PATH=/var/lib/agreemshield/models
```

## Performance

- **Document Processing**: 2-5 seconds for typical PDF
- **Clause Extraction**: 1-2 seconds
- **Risk Classification**: <100ms per clause
- **Total Analysis Time**: 3-8 seconds for typical agreement

## Troubleshooting

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### OCR not working
```bash
# Install Tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: apt-get install tesseract-ocr
# Mac: brew install tesseract
```

### Import errors
```bash
# Reinstall packages
pip install --upgrade -r requirements.txt
```

### Database errors
```bash
# Reset database
rm agreemshield.db
# Restart server (will recreate)
```

## Contributing

1. Add features to appropriate module
2. Update training data if needed
3. Retrain model
4. Add API endpoint if needed
5. Update documentation

## License

MIT License - See LICENSE file

## Support

For issues or questions:
- Create GitHub issue
- Contact: support@agreemshield.ai
