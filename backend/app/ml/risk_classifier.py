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
        Classify risk level of a clause with REAL content analysis
        Returns: risk_level, confidence, explanation based on ACTUAL text
        """
        if not clause_text:
            clause_text = ''
        if not clause_type:
            clause_type = 'General Clause'
        
        # ANALYZE ACTUAL CONTENT - not templates
        content_analysis = self._analyze_actual_content(clause_text, clause_type)
        
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
        
        # Determine final risk based on actual content
        if content_analysis['detected_issues']:
            final_risk = content_analysis['risk_level']
            confidence = content_analysis['confidence']
        elif rule_risk and rule_risk == "High":
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
        
        # Use REAL explanation from content analysis
        explanation = content_analysis['explanation'] if content_analysis['explanation'] else \
                     self._generate_explanation(clause_type, final_risk, startup_type)
        
        return {
            'risk_level': final_risk,
            'confidence': float(confidence),
            'explanation': explanation,
            'detection_method': 'content_analysis' if content_analysis['detected_issues'] else ('ml' if ml_risk else 'rule_based'),
            'detected_issues': content_analysis['detected_issues'],
            'specific_terms': content_analysis['specific_terms']
        }
    
    def _check_high_risk_patterns(self, text: str, clause_type: str) -> str:
        """Check for known high-risk patterns"""
        if clause_type in self.high_risk_patterns:
            for pattern in self.high_risk_patterns[clause_type]:
                if re.search(pattern, text, re.IGNORECASE):
                    return "High"
        return None
    
    def _analyze_actual_content(self, text: str, clause_type: str) -> Dict:
        """Analyze the ACTUAL clause content to generate specific explanations"""
        text_lower = text.lower() if text else ""
        analysis = {
            'risk_level': 'Low',
            'confidence': 0.7,
            'explanation': '',
            'detected_issues': [],
            'specific_terms': []
        }
        
        if not text:
            return analysis
        
        # BOARD CONTROL - Actual analysis
        if 'board' in text_lower or 'director' in text_lower:
            if 'majority' in text_lower and 'investor' in text_lower:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.95
                analysis['explanation'] = "This clause grants investors MAJORITY board control. Based on the actual text, investors can appoint enough directors to outvote founders on ALL decisions including CEO removal, strategic direction, and company sale. This means you could be fired from your own company or forced into an acquisition you don't want."
                analysis['detected_issues'].append("Investor majority board control")
                analysis['detected_issues'].append("Founders can be outvoted on critical decisions")
                analysis['specific_terms'].append("majority")
            elif 'appoint' in text_lower or 'designate' in text_lower:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.85
                analysis['explanation'] = "The clause allows investors to unilaterally appoint board members. This gives them significant control over company governance and decision-making without requiring founder approval."
                analysis['detected_issues'].append("Unilateral investor board appointments")
            elif 'observer' in text_lower:
                analysis['risk_level'] = 'Low'
                analysis['confidence'] = 0.8
                analysis['explanation'] = "This clause grants board observer rights which is standard and low risk. Observers can attend meetings but cannot vote, maintaining founder control while giving investors visibility."
        
        # LIQUIDATION PREFERENCE - Analyze multipliers
        if 'liquidation' in text_lower or 'distribution' in text_lower:
            multipliers = re.findall(r'([2-9])x|([2-9])\s*times', text_lower)
            if multipliers:
                mult_value = multipliers[0][0] or multipliers[0][1]
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.98
                analysis['explanation'] = f"CRITICAL ISSUE: This clause specifies a {mult_value}x liquidation preference. This means investors get {mult_value} times their investment back BEFORE founders see a penny. In a typical $20M exit, if investors put in $5M, they take ${int(mult_value)*5}M first, leaving only ${20-int(mult_value)*5}M for everyone else. This can completely wipe out founder returns."
                analysis['detected_issues'].append(f"{mult_value}x liquidation preference - extremely unfavorable")
                analysis['detected_issues'].append("Founders may receive nothing in modest exits")
                analysis['specific_terms'].append(f"{mult_value}x")
            
            if 'participating' in text_lower and '1x' not in text_lower:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.95
                analysis['explanation'] += " ADDITIONALLY: This is PARTICIPATING preferred stock, meaning investors get paid TWICE - first they get their preference, then they participate in remaining proceeds. This is extremely founder-unfriendly and rare in modern deals."
                analysis['detected_issues'].append("Participating preferred - double dipping")
                analysis['specific_terms'].append("participating")
            elif 'non-participating' in text_lower or 'non participating' in text_lower:
                analysis['risk_level'] = 'Low' if '1x' in text_lower else 'Medium'
                analysis['confidence'] = 0.85
                analysis['explanation'] = "This clause has standard 1x non-participating liquidation preference, which is market standard and fair. Investors get their money back first OR their pro-rata share, whichever is higher - not both."
        
        # ANTI-DILUTION - Check for full ratchet
        if 'anti' in text_lower and 'dilution' in text_lower:
            if 'full ratchet' in text_lower or 'full-ratchet' in text_lower:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.99
                analysis['explanation'] = "EXTREMELY DANGEROUS: Full ratchet anti-dilution detected in actual text. If you raise money at a lower valuation later (down round), investors' shares will be repriced as if they paid the new lower price, MASSIVELY diluting founders. Example: If valuation drops from $10M to $5M, investors effectively get 2x more shares at your expense. This can reduce founder ownership by 30-50% and makes future fundraising nearly impossible. This is considered predatory and almost never seen in legitimate deals."
                analysis['detected_issues'].append("Full ratchet anti-dilution - predatory term")
                analysis['detected_issues'].append("Massive founder dilution in any down-round")
                analysis['detected_issues'].append("Makes future fundraising impossible")
                analysis['specific_terms'].append("full ratchet")
            elif 'weighted average' in text_lower or 'weighted-average' in text_lower:
                if 'broad' in text_lower or 'broad-based' in text_lower:
                    analysis['risk_level'] = 'Low'
                    analysis['confidence'] = 0.9
                    analysis['explanation'] = "Broad-based weighted average anti-dilution is present, which is the market standard and fair. It provides reasonable investor protection while not excessively punishing founders in down-rounds."
                else:
                    analysis['risk_level'] = 'Medium'
                    analysis['confidence'] = 0.8
                    analysis['explanation'] = "Weighted average anti-dilution is present. Confirm this is 'broad-based' (includes option pool) rather than 'narrow-based' for more founder-friendly terms."
                    analysis['detected_issues'].append("Verify if broad-based or narrow-based")
        
        # PRO-RATA RIGHTS
        if 'pro rata' in text_lower or 'pro-rata' in text_lower:
            analysis['risk_level'] = 'Low'
            analysis['confidence'] = 0.85
            analysis['explanation'] = "Pro-rata rights allow investors to maintain their ownership percentage in future rounds by investing proportionally. This is standard, founder-friendly, and actually beneficial as it ensures committed investors can continue supporting the company."
        
        # VESTING
        if 'vesting' in text_lower or 'vest' in text_lower:
            if 'acceleration' not in text_lower:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.9
                analysis['explanation'] = "CRITICAL: This vesting clause contains NO acceleration provisions. If the company is acquired or you're terminated, you forfeit all unvested shares. In a typical 4-year vest, if acquired after 2 years, you lose 50% of your equity - potentially millions of dollars. Founders should always have at least single-trigger acceleration on acquisition."
                analysis['detected_issues'].append("No acceleration clause - lose equity in acquisition")
                analysis['detected_issues'].append("Founder could lose millions in exit")
            elif 'single trigger' in text_lower or 'single-trigger' in text_lower:
                analysis['risk_level'] = 'Low'
                analysis['confidence'] = 0.9
                analysis['explanation'] = "Good: Single-trigger acceleration is present, meaning shares vest immediately upon acquisition. This protects founders' equity value in exit scenarios."
            
            cliff_match = re.search(r'(\d+)\s*(?:year|month)\s*cliff', text_lower)
            if cliff_match:
                cliff_period = cliff_match.group(1)
                if int(cliff_period) > 12 or ('year' in cliff_match.group(0) and int(cliff_period) > 1):
                    analysis['risk_level'] = 'High'
                    analysis['confidence'] = 0.85
                    analysis['explanation'] += f" PROBLEM: {cliff_period} cliff period is too long. Standard is 1 year. Longer cliffs increase risk if you leave or are terminated early."
                    analysis['detected_issues'].append(f"{cliff_period} cliff period - too long")
        
        # IP ASSIGNMENT
        if 'intellectual property' in text_lower or ('ip' in text_lower and 'assign' in text_lower):
            if 'all' in text_lower and ('invention' in text_lower or 'work' in text_lower):
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.9
                analysis['explanation'] = "OVERLY BROAD: This IP assignment clause captures ALL intellectual property and inventions, including prior work and side projects. The actual language states you assign everything to the company, which could prevent you from using your own prior inventions or working on unrelated projects. This limits future opportunities if this venture fails."
                analysis['detected_issues'].append("All IP assigned - includes prior work")
                analysis['detected_issues'].append("Side projects may be claimed by company")
                analysis['detected_issues'].append("Limits future ventures")
            if 'prior' not in text_lower and 'excluded' not in text_lower:
                analysis['risk_level'] = 'High' if analysis['risk_level'] != 'High' else 'High'
                analysis['detected_issues'].append("No carve-out for prior inventions")
        
        # DRAG-ALONG
        if 'drag' in text_lower and 'along' in text_lower:
            if 'minimum' not in text_lower and 'threshold' not in text_lower and 'floor' not in text_lower:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.92
                analysis['explanation'] = "DANGEROUS: Drag-along rights with NO minimum price protection. Investors can force you to sell the company at ANY price, even a fire-sale price well below the company's potential value. You could be forced to sell for $10M when the company could be worth $100M in 2-3 years."
                analysis['detected_issues'].append("No minimum sale price protection")
                analysis['detected_issues'].append("Can be forced into unfavorable acquisition")
            else:
                analysis['risk_level'] = 'Medium'
                analysis['confidence'] = 0.8
                analysis['explanation'] = "Drag-along rights are present with some price protections. Review the specific minimum price thresholds to ensure they're reasonable."
        
        # VOTING RIGHTS
        if 'voting' in text_lower or 'vote' in text_lower or 'approval' in text_lower:
            veto_items = []
            if 'sale' in text_lower or 'acquisition' in text_lower:
                veto_items.append("company sale")
            if 'hire' in text_lower or 'hiring' in text_lower:
                veto_items.append("hiring")
            if 'compensation' in text_lower:
                veto_items.append("compensation")
            if 'expenditure' in text_lower or 'spending' in text_lower:
                veto_items.append("expenditures")
            
            if len(veto_items) > 3:
                analysis['risk_level'] = 'High'
                analysis['confidence'] = 0.88
                analysis['explanation'] = f"EXCESSIVE CONTROL: Investors have veto rights over {len(veto_items)} types of decisions including: {', '.join(veto_items)}. This gives them operational control and will slow down every major decision, making it difficult to run the business efficiently. Investor approval should be limited to truly major decisions like company sale, dissolution, and IP transfers."
                analysis['detected_issues'].append(f"Investor veto on {len(veto_items)} decision types")
                analysis['detected_issues'].append("Operational control granted to investors")
            elif veto_items:
                analysis['risk_level'] = 'Medium'
                analysis['confidence'] = 0.75
                analysis['explanation'] = f"Investor approval required for: {', '.join(veto_items)}. Review if scope is appropriate - should be limited to major corporate actions."
        
        return analysis
    
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
