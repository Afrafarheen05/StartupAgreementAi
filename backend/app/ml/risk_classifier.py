"""
Risk Classifier Module
ML-based risk classification for agreement clauses with training capability
"""
import os
import re
import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib


class RiskClassifier:
    """ML-based risk classification with rule-based enhancements"""
    
    def __init__(self, model_dir='./trained_models'):
        self.model_dir = model_dir
        self.model = None
        self.vectorizer = None
        self.label_encoder = {'High': 2, 'Medium': 1, 'Low': 0}
        self.label_decoder = {2: 'High', 1: 'Medium', 0: 'Low'}
        
        # Rule-based risk indicators
        self.high_risk_patterns = {
            "Liquidation Preference": [
                r'\d+[xX]\s+participating',
                r'[3-9]x\s+preference',
                r'participating\s+preferred'
            ],
            "Anti-Dilution": [
                r'full\s+ratchet',
                r'no\s+(?:exception|carve[- ]out)'
            ],
            "Board Control": [
                r'investor(?:s)?\s+(?:appoint|designate).*majority',
                r'investor.*control.*board',
                r'tie[- ]breaking.*investor'
            ],
            "Vesting": [
                r'no\s+acceleration',
                r'[5-9][- ]year.*vesting',
                r'repurchase.*unvested'
            ],
            "IP Assignment": [
                r'all.*IP.*to.*company',
                r'prior.*invention',
                r'side.*project'
            ],
            "Drag-Along Rights": [
                r'forced\s+to\s+sell',
                r'no\s+minimum\s+price',
                r'any\s+price'
            ]
        }
        
        # Try to load existing model
        self._load_model()
    
    def train_from_csv(self, csv_path: str) -> Dict:
        """
        Train model from labeled CSV data
        CSV should have: clause_text, clause_type, risk_level
        """
        print(f"Loading training data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Prepare data
        X = df['clause_text'].values
        y = df['risk_level'].map(self.label_encoder).values
        
        # Create feature combinations
        features = self._create_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print("Training model...")
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.2%}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['Low', 'Medium', 'High']))
        
        # Save model
        self._save_model()
        
        return {
            'accuracy': accuracy,
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def _create_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create features for ML model"""
        # TF-IDF on text
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 3),
            stop_words='english'
        )
        text_features = self.vectorizer.fit_transform(df['clause_text']).toarray()
        
        # Clause type one-hot encoding
        clause_types = pd.get_dummies(df['clause_type']).values
        
        # Combine features
        features = np.hstack([text_features, clause_types])
        
        return features
    
    def classify_risk(self, clause_text: str, clause_type: str, startup_type: str = "SaaS") -> Dict:
        """
        Classify risk level of a clause
        Returns: risk_level, confidence, explanation
        """
        if not clause_text:
            clause_text = ''
        if not clause_type:
            clause_type = 'General Clause'
        
        # Rule-based classification for high-risk patterns
        rule_risk = self._check_high_risk_patterns(clause_text, clause_type)
        
        # ML-based classification if model is trained
        ml_risk = None
        ml_confidence = 0.0
        
        if self.model and self.vectorizer:
            try:
                # Create feature vector
                text_features = self.vectorizer.transform([clause_text]).toarray()
                
                # Create clause type features
                clause_type_features = np.zeros(15)  # Adjust based on training
                
                # Combine features
                features = np.hstack([text_features, clause_type_features.reshape(1, -1)])
                
                # Predict
                prediction = self.model.predict(features)[0]
                probabilities = self.model.predict_proba(features)[0]
                
                ml_risk = self.label_decoder[prediction]
                ml_confidence = probabilities[prediction]
                
            except Exception as e:
                print(f"ML prediction failed: {e}")
                ml_risk = None
        
        # Combine rule-based and ML predictions
        if rule_risk and rule_risk == "High":
            final_risk = "High"
            confidence = 0.9
        elif ml_risk:
            final_risk = ml_risk
            confidence = ml_confidence
        else:
            # Fallback to heuristic-based classification
            final_risk = self._heuristic_classification(clause_text, clause_type, 
                                                       startup_type)
            confidence = 0.7
        
        # Context-based adjustment
        final_risk = self._adjust_for_context(final_risk, clause_type, 
                                              startup_type)
        
        # Generate explanation
        explanation = self._generate_explanation(clause_type, final_risk, 
                                                startup_type)
        
        return {
            'risk_level': final_risk,
            'confidence': float(confidence),
            'explanation': explanation,
            'detection_method': 'ml' if ml_risk else 'rule_based'
        }
    
    def _check_high_risk_patterns(self, text: str, clause_type: str) -> str:
        """Check for known high-risk patterns"""
        if clause_type in self.high_risk_patterns:
            for pattern in self.high_risk_patterns[clause_type]:
                if re.search(pattern, text, re.IGNORECASE):
                    return "High"
        return None
    
    def _heuristic_classification(self, text: str, clause_type: str,
                                  startup_type: str) -> str:
        """Heuristic-based classification when ML is not available"""
        text_lower = text.lower()
        
        # High-risk clause types
        high_risk_types = ['Liquidation Preference', 'Anti-Dilution', 'Board Control', 
                          'Drag-Along Rights', 'Voting Rights']
        
        if clause_type in high_risk_types:
            # Check for extreme terms
            if any(term in text_lower for term in ['force', 'require', 'must', 
                                                     'control', 'majority', 'all']):
                return "High"
            return "Medium"
        
        # Low-risk clause types
        low_risk_types = ['Information Rights', 'Pro-Rata Rights', 'Pay-to-Play']
        if clause_type in low_risk_types:
            return "Low"
        
        # Default to Medium
        return "Medium"
    
    def _adjust_for_context(self, base_risk: str, clause_type: str,
                           startup_type: str) -> str:
        """Adjust risk based on startup context"""
        
        # Industry-specific adjustments
        if startup_type == 'healthtech' and clause_type == 'IP Assignment' and base_risk == 'Low':
            return 'Medium'
        
        if startup_type == 'fintech' and clause_type == 'Voting Rights' and base_risk == 'Medium':
            return 'High'
        
        return base_risk
    
    def _generate_explanation(self, clause_type: str, risk_level: str,
                             startup_type: str) -> str:
        """Generate human-readable explanation of risk"""
        
        explanations = {
            "Liquidation Preference": {
                "High": "Extremely unfavorable terms. Investor takes disproportionate share of exit proceeds, potentially leaving founders with nothing.",
                "Medium": "Standard protection for investors but could impact founder returns in modest exits.",
                "Low": "Fair and balanced liquidation terms following market standards."
            },
            "Anti-Dilution": {
                "High": "Full ratchet or harsh terms that can severely dilute founders in down-rounds. Negotiate to weighted average.",
                "Medium": "Standard anti-dilution protection. May cause some dilution in down-rounds.",
                "Low": "Founder-friendly anti-dilution terms or reasonable protections."
            },
            "Board Control": {
                "High": "Founders lose control of the company. Investors can make unilateral decisions.",
                "Medium": "Balanced board composition but investor influence is significant.",
                "Low": "Founder-controlled board with investor observer rights or minority representation."
            },
            "Vesting": {
                "High": "Harsh vesting terms with long cliff periods or limited acceleration. Risk of losing equity if removed.",
                "Medium": "Standard 4-year vesting with 1-year cliff. Common but limits founder flexibility.",
                "Low": "Accelerated vesting or founder-friendly terms."
            },
            "IP Assignment": {
                "High": "Overly broad IP assignment including personal projects and prior work. Limits future opportunities.",
                "Medium": "Standard IP assignment for work related to company business.",
                "Low": "Limited IP assignment with clear carve-outs for prior and unrelated work."
            },
            "Drag-Along Rights": {
                "High": "Can be forced to sell at any price. No minimum threshold protection.",
                "Medium": "Standard drag-along with some price protections.",
                "Low": "Well-protected with minimum price thresholds and founder approval rights."
            }
        }
        
        default_explanation = {
            "High": f"This {clause_type} clause contains unfavorable terms that significantly impact founder rights and equity.",
            "Medium": f"This {clause_type} clause is fairly standard but requires careful consideration.",
            "Low": f"This {clause_type} clause appears reasonable and balanced."
        }
        
        explanation = explanations.get(clause_type, default_explanation).get(risk_level, 
                                                                             default_explanation[risk_level])
        
        return explanation
    
    def _save_model(self):
        """Save trained model to disk"""
        os.makedirs(self.model_dir, exist_ok=True)
        
        model_path = os.path.join(self.model_dir, 'risk_classifier.pkl')
        vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)
        
        print(f"Model saved to {model_path}")
    
    def _load_model(self):
        """Load trained model from disk"""
        model_path = os.path.join(self.model_dir, 'risk_classifier.pkl')
        vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                print("Loaded existing risk classification model")
            except Exception as e:
                print(f"Failed to load model: {e}")
                self.model = None
                self.vectorizer = None
