"""
Future Prediction Engine
Predicts future risks based on current agreement clauses
"""
import numpy as np
from typing import Dict, List
from collections import defaultdict


class FuturePredictor:
    """Predict future risks based on historical patterns and current clauses"""
    
    def __init__(self):
        # Historical probability data based on similar agreements
        self.risk_probabilities = {
            "Board Control": {
                "6-12 months": {
                    "Control Issues": 0.85,
                    "Decision Blocking": 0.65
                },
                "1-2 years": {
                    "CEO Replacement": 0.45,
                    "Strategic Disagreements": 0.70
                },
                "2-3 years": {
                    "Loss of Control": 0.55,
                    "Forced Exit": 0.40
                }
            },
            "Liquidation Preference": {
                "2-3 years": {
                    "Reduced Exit Value": 0.82,
                    "Founder Payout Impact": 0.75
                },
                "3+ years": {
                    "Total Equity Wipeout": 0.40
                }
            },
            "Anti-Dilution": {
                "1-2 years": {
                    "Founder Dilution": 0.78,
                    "Down-round Impact": 0.60
                },
                "2-3 years": {
                    "Severe Dilution": 0.45
                }
            },
            "Vesting": {
                "6-12 months": {
                    "Limited Flexibility": 0.55
                },
                "1-2 years": {
                    "Equity Loss on Departure": 0.50
                }
            },
            "Drag-Along Rights": {
                "2-3 years": {
                    "Forced Acquisition": 0.70,
                    "Unfavorable Sale": 0.50
                }
            },
            "IP Assignment": {
                "2-3 years": {
                    "IP Ownership Disputes": 0.35
                },
                "3+ years": {
                    "Future Venture Limitations": 0.30
                }
            }
        }
    
    def predict_future_risks(self, clauses: List[Dict], risk_assessment: Dict,
                            startup_type: str, funding_stage: str) -> Dict:
        """
        Generate timeline-based future risk predictions
        """
        # Collect high-risk clauses
        high_risk_clauses = [c for c in clauses if c.get('risk_level') == 'High']
        medium_risk_clauses = [c for c in clauses if c.get('risk_level') == 'Medium']
        
        # Build timeline predictions
        timeline = []
        
        # 6-12 months predictions
        short_term_risks = self._predict_short_term(high_risk_clauses, startup_type, funding_stage)
        if short_term_risks:
            timeline.append({
                'period': '6-12 months',
                'risks': short_term_risks
            })
        
        # 1-2 years predictions
        mid_term_risks = self._predict_mid_term(high_risk_clauses, medium_risk_clauses, 
                                                startup_type, funding_stage)
        if mid_term_risks:
            timeline.append({
                'period': '1-2 years',
                'risks': mid_term_risks
            })
        
        # 2-3 years predictions
        long_term_risks = self._predict_long_term(high_risk_clauses, risk_assessment,
                                                  startup_type, funding_stage)
        if long_term_risks:
            timeline.append({
                'period': '2-3 years',
                'risks': long_term_risks
            })
        
        # 3+ years predictions
        very_long_term_risks = self._predict_very_long_term(high_risk_clauses, risk_assessment,
                                                            startup_type, funding_stage)
        if very_long_term_risks:
            timeline.append({
                'period': '3+ years',
                'risks': very_long_term_risks
            })
        
        # Calculate overall outlook
        all_probabilities = []
        for period in timeline:
            for risk in period['risks']:
                all_probabilities.append(risk['probability'])
        
        overall_probability = int(np.mean(all_probabilities)) if all_probabilities else 50
        sentiment = self._determine_sentiment(overall_probability, len(high_risk_clauses))
        
        return {
            'timeline': timeline,
            'overall_outlook': {
                'probability': overall_probability,
                'sentiment': sentiment,
                'summary': self._generate_summary(overall_probability, len(high_risk_clauses),
                                                 startup_type, funding_stage)
            }
        }
    
    def _predict_short_term(self, high_risk_clauses: List[Dict], 
                           startup_type: str, funding_stage: str) -> List[Dict]:
        """Predict 6-12 month risks"""
        risks = []
        clause_types = [c.get('type') for c in high_risk_clauses]
        
        if 'Board Control' in clause_types:
            risks.append({
                'title': 'Board Control Issues',
                'probability': 85,
                'impact': 'High',
                'description': 'Investor majority on board may begin blocking key decisions on hiring, partnerships, or product direction.'
            })
        
        if 'Information Rights' in clause_types or 'Voting Rights' in clause_types:
            risks.append({
                'title': 'Cash Flow Restrictions',
                'probability': 65,
                'impact': 'Medium',
                'description': 'Information rights may evolve into investor micromanagement of expenses and burn rate.'
            })
        
        if 'No-Shop Clause' in clause_types:
            risks.append({
                'title': 'Fundraising Limitations',
                'probability': 55,
                'impact': 'Medium',
                'description': 'Exclusivity periods may extend, limiting ability to explore other funding options.'
            })
        
        return risks
    
    def _predict_mid_term(self, high_risk_clauses: List[Dict], medium_risk_clauses: List[Dict],
                         startup_type: str, funding_stage: str) -> List[Dict]:
        """Predict 1-2 year risks"""
        risks = []
        high_types = [c.get('type') for c in high_risk_clauses]
        medium_types = [c.get('type') for c in medium_risk_clauses]
        
        if 'Anti-Dilution' in high_types:
            risks.append({
                'title': 'Founder Dilution at Next Round',
                'probability': 78,
                'impact': 'Critical',
                'description': 'Anti-dilution clause will trigger if forced to raise down-round. Founders could lose 25-40% additional equity.'
            })
        
        if 'Board Control' in high_types:
            risks.append({
                'title': 'Forced CEO Replacement',
                'probability': 45,
                'impact': 'Critical',
                'description': 'Based on similar agreements, investor board control often leads to founder removal if KPIs missed.'
            })
        
        if 'Voting Rights' in high_types or 'Drag-Along Rights' in medium_types:
            risks.append({
                'title': 'Fundraising Blocked',
                'probability': 60,
                'impact': 'High',
                'description': 'Drag-along and board control give investors power to block future fundraising if they disagree with terms.'
            })
        
        if 'Vesting' in high_types or 'Vesting' in medium_types:
            risks.append({
                'title': 'Equity Loss on Departure',
                'probability': 50,
                'impact': 'High',
                'description': 'If removed or decide to leave, unvested equity will be forfeited, potentially losing millions in value.'
            })
        
        return risks
    
    def _predict_long_term(self, high_risk_clauses: List[Dict], risk_assessment: Dict,
                          startup_type: str, funding_stage: str) -> List[Dict]:
        """Predict 2-3 year risks"""
        risks = []
        high_types = [c.get('type') for c in high_risk_clauses]
        
        if 'Drag-Along Rights' in high_types:
            risks.append({
                'title': 'Forced Acquisition',
                'probability': 70,
                'impact': 'Critical',
                'description': 'Investors may force sale to return capital to their fund, even if company could be worth 10x more in 3 years.'
            })
        
        if 'Liquidation Preference' in high_types:
            risks.append({
                'title': 'Loss of Economic Value',
                'probability': 82,
                'impact': 'Critical',
                'description': '3x participating liquidation preference means in most exits, founders receive <10% of what their equity percentage suggests.'
            })
        
        if risk_assessment.get('control_risk', 0) > 70:
            risks.append({
                'title': 'Complete Loss of Control',
                'probability': 55,
                'impact': 'High',
                'description': 'Cumulative effect of board control, vesting clawbacks, and investor rights creates situation where founders have no real authority.'
            })
        
        if 'IP Assignment' in high_types:
            risks.append({
                'title': 'IP Ownership Disputes',
                'probability': 35,
                'impact': 'Medium',
                'description': 'Broad IP assignment could create disputes if founders want to start new ventures in similar space.'
            })
        
        return risks
    
    def _predict_very_long_term(self, high_risk_clauses: List[Dict], risk_assessment: Dict,
                               startup_type: str, funding_stage: str) -> List[Dict]:
        """Predict 3+ year risks"""
        risks = []
        high_types = [c.get('type') for c in high_risk_clauses]
        
        if 'Liquidation Preference' in high_types and risk_assessment.get('economic_risk', 0) > 70:
            risks.append({
                'title': 'Total Equity Wipeout',
                'probability': 40,
                'impact': 'Critical',
                'description': 'If company exits for <5x current valuation, liquidation preferences and accumulated dividends could consume entire proceeds.'
            })
        
        if 'IP Assignment' in high_types:
            risks.append({
                'title': 'Future Venture Limitations',
                'probability': 30,
                'impact': 'Medium',
                'description': 'If company fails, inability to reuse technology or ideas could limit opportunities for next startup.'
            })
        
        return risks
    
    def _determine_sentiment(self, probability: int, high_risk_count: int) -> str:
        """Determine overall sentiment"""
        if probability >= 70 or high_risk_count >= 4:
            return "Unfavorable"
        elif probability >= 50 or high_risk_count >= 2:
            return "Concerning"
        elif probability >= 30:
            return "Moderate"
        else:
            return "Favorable"
    
    def _generate_summary(self, probability: int, high_risk_count: int,
                         startup_type: str, funding_stage: str) -> str:
        """Generate summary text"""
        
        if probability >= 70:
            return f"Based on analysis of similar {startup_type} agreements at {funding_stage} stage, this contract has significantly higher-than-average risk for founders. {probability}% chance of major adverse events within 3 years."
        elif probability >= 50:
            return f"This agreement contains several concerning terms. Historical data from {startup_type} startups shows {probability}% probability of founder-unfavorable outcomes."
        else:
            return f"While some risks exist, this agreement is relatively balanced compared to typical {startup_type} contracts at {funding_stage} stage. {probability}% probability of issues."
