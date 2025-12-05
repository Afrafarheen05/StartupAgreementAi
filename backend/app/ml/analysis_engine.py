"""
Analysis Engine
Orchestrates the entire ML pipeline for document analysis
"""
import os
from typing import Dict, Optional
from datetime import datetime

from .document_processor import DocumentProcessor
from .clause_extractor import ClauseExtractor
from .risk_classifier import RiskClassifier
from .future_predictor import FuturePredictor
from .recommendation_engine import RecommendationEngine


class AnalysisEngine:
    """Main engine that orchestrates document analysis"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize all ML components"""
        self.document_processor = DocumentProcessor()
        self.clause_extractor = ClauseExtractor()
        self.risk_classifier = RiskClassifier(model_path)
        self.future_predictor = FuturePredictor()
        self.recommendation_engine = RecommendationEngine()
    
    def analyze_document(self, file_path: str, startup_type: str = "SaaS") -> Dict:
        """
        Analyze a document and return comprehensive results
        
        Args:
            file_path: Path to uploaded document (PDF or DOCX)
            startup_type: Type of startup for context-specific analysis
            
        Returns:
            Complete analysis with clauses, risks, predictions, and recommendations
        """
        try:
            # Step 1: Extract text from document
            print(f"Processing document: {file_path}")
            doc_result = self.document_processor.process_document(file_path)
            
            if not doc_result['success']:
                return {
                    'success': False,
                    'error': doc_result.get('error', 'Failed to process document')
                }
            
            text = doc_result['text']
            sections = doc_result.get('sections', [])  # Sections are optional
            
            # Step 2: Extract clauses
            print("Extracting clauses...")
            extracted_clauses = self.clause_extractor.extract_clauses(text, sections)
            
            # Step 3: Classify risk for each clause
            print("Classifying risks...")
            for clause in extracted_clauses:
                risk_result = self.risk_classifier.classify_risk(
                    clause['text'],
                    clause['type'],
                    startup_type
                )
                clause.update(risk_result)
            
            # Step 4: Calculate overall risk metrics
            risk_assessment = self._calculate_risk_metrics(extracted_clauses)
            
            # Step 5: Generate future predictions
            print("Generating predictions...")
            predictions = self.future_predictor.predict_future_risks(
                extracted_clauses,
                risk_assessment,
                startup_type,
                "seed"  # Default funding stage
            )
            
            # Step 6: Generate recommendations
            print("Generating recommendations...")
            recommendations = self.recommendation_engine.generate_recommendations(
                extracted_clauses,
                risk_assessment
            )
            
            # Step 7: Compile comprehensive results
            result = {
                'success': True,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'document_info': {
                    'filename': os.path.basename(file_path),
                    'page_count': doc_result.get('pages', 0),
                    'word_count': len(text.split())
                },
                'clauses': extracted_clauses,
                'risk_assessment': risk_assessment,
                'riskAssessment': risk_assessment,  # Camel case for frontend compatibility
                'future_predictions': predictions,
                'futurePredictions': predictions,  # Camel case for frontend compatibility
                'recommendations': recommendations,
                'startup_type': startup_type,
                'summary': {
                    'total': risk_assessment.get('clause_count', 0),
                    'high': risk_assessment.get('risk_distribution', {}).get('High', 0),
                    'medium': risk_assessment.get('risk_distribution', {}).get('Medium', 0),
                    'low': risk_assessment.get('risk_distribution', {}).get('Low', 0)
                },
                'metadata': {
                    'startupType': startup_type,
                    'fundingStage': 'seed'
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    def _calculate_risk_metrics(self, clauses: list) -> Dict:
        """Calculate overall risk assessment metrics"""
        if not clauses:
            return {
                'overall_score': 0,
                'overall_level': 'Unknown',
                'risk_distribution': {'High': 0, 'Medium': 0, 'Low': 0},
                'clause_count': 0,
                'dangerous_clauses': []
            }
        
        # Count risk levels
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for clause in clauses:
            risk_level = clause.get('risk_level', 'Low')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Calculate weighted risk score (0-100)
        total = len(clauses)
        # INVERTED SCALE: Lower score = Higher risk (founder-friendly scoring)
        # High risk clauses REDUCE the score, Low risk clauses INCREASE it
        risk_score = (
            (risk_counts['Low'] * 100) +
            (risk_counts['Medium'] * 50) +
            (risk_counts['High'] * 10)
        ) / total if total > 0 else 0
        
        # Determine overall level (inverted: low score = high risk)
        if risk_score < 40:
            overall_level = 'High'
        elif risk_score < 70:
            overall_level = 'Medium'
        else:
            overall_level = 'Low'
        
        # Identify dangerous clauses
        dangerous_clauses = [
            {
                'type': c['type'],
                'risk_level': c['risk_level'],
                'risk_score': c.get('risk_score', 0),
                'concern': c.get('explanation', 'Requires careful review')
            }
            for c in clauses 
            if c.get('risk_level') == 'High'
        ]
        
        # Categorize risks by type
        risk_categories = self._categorize_risks(clauses)
        
        # Calculate statistics by clause type
        clause_types = {}
        for clause in clauses:
            ctype = clause['type']
            if ctype not in clause_types:
                clause_types[ctype] = {
                    'count': 0,
                    'risk_levels': {'High': 0, 'Medium': 0, 'Low': 0}
                }
            clause_types[ctype]['count'] += 1
            clause_types[ctype]['risk_levels'][clause.get('risk_level', 'Low')] += 1
        
        return {
            'overall_score': round(risk_score, 1),
            'overall_level': overall_level,
            'risk_distribution': risk_counts,
            'clause_count': total,
            'dangerous_clauses': dangerous_clauses,
            'clause_types': clause_types,
            'red_flags': len(dangerous_clauses),
            'risk_categories': risk_categories,
            'summary': self._generate_risk_summary(risk_score, risk_counts)
        }
    
    def _categorize_risks(self, clauses: list) -> Dict:
        """Categorize risks into operational, regulatory, and financial"""
        categories = {
            'operational': {'count': 0, 'severity': 'Low', 'clauses': []},
            'regulatory': {'count': 0, 'severity': 'Low', 'clauses': []},
            'financial': {'count': 0, 'severity': 'Low', 'clauses': []}
        }
        
        # Map clause types to risk categories
        operational_types = ['Board Control', 'Voting Rights', 'Management Rights', 
                           'Information Rights', 'Vesting', 'Employment Terms']
        regulatory_types = ['Compliance Obligations', 'Regulatory Restrictions', 
                          'IP Assignment', 'Non-Compete', 'Confidentiality']
        financial_types = ['Liquidation Preference', 'Anti-Dilution', 'Valuation',
                         'Investment Amount', 'Pay-to-Play', 'Pro-Rata Rights',
                         'Drag-Along Rights', 'Conversion Rights']
        
        for clause in clauses:
            ctype = clause.get('type', '')
            risk_level = clause.get('risk_level', 'Low')
            
            if ctype in operational_types:
                categories['operational']['count'] += 1
                if risk_level == 'High':
                    categories['operational']['clauses'].append(clause)
                    categories['operational']['severity'] = 'High'
                elif risk_level == 'Medium' and categories['operational']['severity'] != 'High':
                    categories['operational']['severity'] = 'Medium'
                    
            elif ctype in regulatory_types:
                categories['regulatory']['count'] += 1
                if risk_level == 'High':
                    categories['regulatory']['clauses'].append(clause)
                    categories['regulatory']['severity'] = 'High'
                elif risk_level == 'Medium' and categories['regulatory']['severity'] != 'High':
                    categories['regulatory']['severity'] = 'Medium'
                    
            elif ctype in financial_types:
                categories['financial']['count'] += 1
                if risk_level == 'High':
                    categories['financial']['clauses'].append(clause)
                    categories['financial']['severity'] = 'High'
                elif risk_level == 'Medium' and categories['financial']['severity'] != 'High':
                    categories['financial']['severity'] = 'Medium'
        
        return categories
    
    def _generate_risk_summary(self, score: float, distribution: Dict) -> str:
        """Generate human-readable risk summary"""
        high = distribution['High']
        medium = distribution['Medium']
        
        if score >= 70:
            return f"⚠️ High Risk Agreement: {high} critical clauses require immediate attention. Strongly recommend legal review before signing."
        elif score >= 50:
            return f"⚠️ Moderate-High Risk: {high} high-risk and {medium} medium-risk clauses detected. Negotiate key terms before proceeding."
        elif score >= 30:
            return f"⚡ Moderate Risk: Agreement has {medium} areas needing negotiation. Generally acceptable with modifications."
        else:
            return f"✓ Low Risk: Agreement appears founder-friendly with standard market terms."
    
    def train_model(self, csv_path: str) -> Dict:
        """Train the risk classification model"""
        try:
            print(f"Training model from: {csv_path}")
            result = self.risk_classifier.train_from_csv(csv_path)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
