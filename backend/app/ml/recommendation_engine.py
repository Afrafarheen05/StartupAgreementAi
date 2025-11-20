"""
Recommendation Engine
Generates actionable recommendations for risky clauses
"""
from typing import Dict, List


class RecommendationEngine:
    """Generate actionable recommendations for clause negotiation"""
    
    def __init__(self):
        # Pre-defined recommendation templates
        self.recommendations_db = {
            "Liquidation Preference": {
                "High": {
                    "issue": "Extremely unfavorable liquidation terms (3x+ participating)",
                    "recommendation": "MUST negotiate to 1x non-participating. This is non-negotiable for protecting founder value.",
                    "tips": [
                        "Show comparables from similar deals in your sector - 1x non-participating is market standard",
                        "Explain that participating preference misaligns incentives - investors profit even from mediocre exits",
                        "Offer to accept 1.5x non-participating as compromise if investor strongly resists",
                        "Calculate and show investor how participating preference reduces their upside in successful exits"
                    ],
                    "impact": "Could increase founder payout by $2-5M in typical exit scenarios"
                },
                "Medium": {
                    "issue": "Standard but could be optimized",
                    "recommendation": "If 2x preference, negotiate down to 1x or ensure it's non-participating",
                    "tips": [
                        "Request non-participating preference to align incentives",
                        "Ask for cap on liquidation preference at certain exit values",
                        "Propose that preference expires after certain time period or funding milestone"
                    ],
                    "impact": "Could improve founder returns by 15-30% in exit scenarios"
                }
            },
            "Anti-Dilution": {
                "High": {
                    "issue": "Full ratchet will cause massive founder dilution in down rounds",
                    "recommendation": "Change to broad-based weighted average anti-dilution, or remove entirely for seed stage",
                    "tips": [
                        "Explain that full ratchet is outdated and rarely used in modern deals",
                        "Weighted average is fair protection that doesn't excessively punish founders",
                        "If investor insists, add carve-outs for option pools and small insider rounds",
                        "Show data that full ratchet makes future fundraising nearly impossible"
                    ],
                    "impact": "Could save 15-30% founder equity in future financing scenarios"
                },
                "Medium": {
                    "issue": "Weighted average is standard but could have better terms",
                    "recommendation": "Ensure it's broad-based (not narrow-based) weighted average with reasonable carve-outs",
                    "tips": [
                        "Request carve-outs for option pool increases",
                        "Exclude small strategic investments from anti-dilution calculations",
                        "Add minimum threshold before anti-dilution triggers (e.g., only if down >20%)"
                    ],
                    "impact": "Reduces dilution impact by 5-10% in down-round scenarios"
                }
            },
            "Board Control": {
                "High": {
                    "issue": "Investor majority control removes founder autonomy",
                    "recommendation": "Negotiate for balanced board: 2 founder seats, 1 investor seat, 2 independent seats",
                    "tips": [
                        "Frame as risk mitigation for investor - founder-led companies perform better statistically",
                        "Propose independent directors with relevant industry expertise as compromise",
                        "Include founder-approval requirements (supermajority) for critical decisions like CEO removal, sale, or IP",
                        "Show examples of successful companies that maintained founder board control"
                    ],
                    "impact": "Maintains strategic control and prevents forced exits or CEO replacement"
                },
                "Medium": {
                    "issue": "Board composition could be more founder-friendly",
                    "recommendation": "Negotiate for at least equal board representation or protective provisions",
                    "tips": [
                        "Request founder approval for major decisions even if board is balanced",
                        "Add requirement that independent directors must be mutually agreed upon",
                        "Include provisions that certain decisions require founder consent"
                    ],
                    "impact": "Preserves founder influence over key strategic decisions"
                }
            },
            "Vesting": {
                "High": {
                    "issue": "Harsh vesting terms with long cliff or no acceleration",
                    "recommendation": "Negotiate single-trigger acceleration for 50% of shares and shorter cliff (6 months)",
                    "tips": [
                        "Explain that harsh vesting discourages you from fighting for best exit",
                        "Request double-trigger acceleration: 50% single-trigger + 50% double-trigger",
                        "For founding team, negotiate that some equity is fully vested immediately",
                        "Add provision that vesting continues during disability or parental leave"
                    ],
                    "impact": "Protects $500K-$2M in equity value if forced out or in acquisition"
                },
                "Medium": {
                    "issue": "Standard 4-year vesting but could use acceleration protections",
                    "recommendation": "Add acceleration provisions for change of control or involuntary termination",
                    "tips": [
                        "Request at least 25% immediate acceleration on acquisition",
                        "Add acceleration if title, role, or compensation changes post-acquisition",
                        "Include that vesting continues during short-term disability"
                    ],
                    "impact": "Provides protection worth $200K-$1M in acquisition scenarios"
                }
            },
            "Drag-Along Rights": {
                "High": {
                    "issue": "Can be forced into unfavorable acquisition at any price",
                    "recommendation": "Add minimum price threshold (2x last round valuation) and founder approval for sales under $50M",
                    "tips": [
                        "Frame as ensuring quality exits that benefit all parties",
                        "Show examples where forced fire-sales destroyed value for everyone",
                        "Compromise: lower threshold for acquisitions by strategic buyers vs financial buyers",
                        "Add requirement that sale price must exceed certain multiple of revenue or equity raised"
                    ],
                    "impact": "Prevents forced sales that don't meet founder vision or economic goals"
                },
                "Medium": {
                    "issue": "Standard drag-along but lacks protections",
                    "recommendation": "Add reasonable protections like minimum price thresholds",
                    "tips": [
                        "Request that drag-along only applies if offer exceeds certain valuation",
                        "Add requirement for reasonable notice period before drag-along can be exercised",
                        "Include that founders receive same terms as investors in sale"
                    ],
                    "impact": "Provides safety net against fire-sale exits"
                }
            },
            "IP Assignment": {
                "High": {
                    "issue": "Overly broad - includes pre-existing and unrelated work",
                    "recommendation": "Carve out pre-existing IP and side projects unrelated to company business",
                    "tips": [
                        "Document what IP you're bringing to company vs creating for company",
                        "Standard practice is to only assign IP created as part of employment/founder duties",
                        "Offer detailed schedule of excluded IP to provide clarity and avoid future disputes",
                        "Add provision allowing side projects in different fields with prior board approval"
                    ],
                    "impact": "Preserves ability to use prior work in future ventures if this startup fails"
                },
                "Medium": {
                    "issue": "Standard but could be more specific",
                    "recommendation": "Add clear definitions and carve-outs",
                    "tips": [
                        "Define what constitutes 'company business' to limit scope",
                        "Add exception for general knowledge and skills acquired",
                        "Request that pre-existing IP list can be updated within first 90 days"
                    ],
                    "impact": "Provides flexibility for future ventures"
                }
            },
            "No-Shop Clause": {
                "High": {
                    "issue": "90+ days exclusivity is too long, creates leverage imbalance",
                    "recommendation": "Reduce to 30 days with no automatic extensions",
                    "tips": [
                        "Explain that shorter period incentivizes investor to move quickly",
                        "30 days is standard for completing due diligence in seed rounds",
                        "Offer weekly updates to investor to maintain transparency during exclusivity",
                        "Add provision that exclusivity automatically terminates if investor hasn't provided term sheet"
                    ],
                    "impact": "Maintains optionality and prevents getting stuck in prolonged negotiations"
                },
                "Medium": {
                    "issue": "Standard period but could have better terms",
                    "recommendation": "Add conditions for early termination",
                    "tips": [
                        "Request that exclusivity ends if investor doesn't maintain engagement",
                        "Add provision allowing termination if investor changes proposed terms materially",
                        "Include that any extension requires mutual written agreement"
                    ],
                    "impact": "Provides flexibility if deal isn't progressing"
                }
            },
            "Voting Rights": {
                "High": {
                    "issue": "Investor veto rights over too many decisions",
                    "recommendation": "Limit veto rights to truly major decisions (sale, dissolution, IP sale)",
                    "tips": [
                        "Agree to veto on major items but remove from operational decisions",
                        "Define clear thresholds (e.g., only transactions >$X need approval)",
                        "Add that veto rights expire if investor doesn't participate in future rounds",
                        "Include that unreasonable withholding of consent allows founders to proceed"
                    ],
                    "impact": "Maintains day-to-day operational freedom"
                },
                "Medium": {
                    "issue": "Standard but could be more balanced",
                    "recommendation": "Add reciprocal rights or sunset provisions",
                    "tips": [
                        "Request that some decisions also require founder supermajority",
                        "Add that investor voting rights reduce proportionally as ownership dilutes",
                        "Include fiduciary duty provisions for investor board members"
                    ],
                    "impact": "Creates more balanced power structure"
                }
            }
        }
    
    def generate_recommendations(self, clauses: List[Dict], 
                                risk_assessment: Dict) -> List[Dict]:
        """Generate prioritized recommendations for risky clauses"""
        recommendations = []
        
        # Sort clauses by risk level
        high_risk = [c for c in clauses if c.get('risk_level') == 'High']
        medium_risk = [c for c in clauses if c.get('risk_level') == 'Medium']
        
        # Generate recommendations for high-risk clauses (Critical priority)
        for clause in high_risk:
            rec = self._create_recommendation(clause, 'Critical')
            if rec:
                recommendations.append(rec)
        
        # Generate recommendations for medium-risk clauses (High/Medium priority)
        for clause in medium_risk[:3]:  # Limit to top 3 medium risks
            rec = self._create_recommendation(clause, 'High')
            if rec:
                recommendations.append(rec)
        
        return recommendations
    
    def _create_recommendation(self, clause: Dict, priority: str) -> Dict:
        """Create detailed recommendation for a specific clause"""
        clause_type = clause.get('type', 'General Clause')
        risk_level = clause.get('risk_level', 'Medium')
        
        # Look up template
        template = self.recommendations_db.get(clause_type, {}).get(risk_level)
        
        if not template:
            # Generate generic recommendation
            template = self._generate_generic_recommendation(clause_type, risk_level)
        
        return {
            'priority': priority,
            'clause': clause_type,
            'issue': template.get('issue', 'Requires attention'),
            'recommendation': template.get('recommendation', 'Negotiate more favorable terms'),
            'negotiation_tips': template.get('tips', []),
            'expected_impact': template.get('impact', 'Improves founder protection')
        }
    
    def _generate_generic_recommendation(self, clause_type: str, risk_level: str) -> Dict:
        """Generate generic recommendation for clause types not in database"""
        if risk_level == 'High':
            return {
                'issue': f"This {clause_type} clause contains unfavorable terms",
                'recommendation': f"Negotiate more balanced {clause_type} terms or add protective provisions",
                'tips': [
                    "Research market standards for this clause type in your industry",
                    "Consult with legal advisor on specific risks",
                    "Request modifications that align with standard practices",
                    "Consider proposing alternative language that addresses investor concerns while protecting founders"
                ],
                'impact': "Reduces risk and improves founder protections"
            }
        else:
            return {
                'issue': f"Standard {clause_type} terms with room for improvement",
                'recommendation': f"Consider requesting minor modifications to {clause_type} terms",
                'tips': [
                    "Review comparable agreements to identify optimization opportunities",
                    "Focus negotiation energy on higher-priority issues first",
                    "If investor resists, may be acceptable to proceed as-is"
                ],
                'impact': "Marginal improvement in terms"
            }
