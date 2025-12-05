"""
Recommendation Engine
Generates actionable recommendations for risky clauses
"""
import re
import os
from typing import Dict, List
import google.generativeai as genai


class RecommendationEngine:
    """Generate actionable recommendations for clause negotiation"""
    
    def __init__(self):
        """Initialize recommendation engine with Gemini AI"""
        # Initialize Gemini for intelligent clause analysis
        self.model = None
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key.strip() != "" and api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("✅ Recommendation Engine: Gemini AI enabled for clause analysis")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed in RecommendationEngine: {e}")
                self.model = None
        else:
            print("⚠️  Recommendation Engine: Running without Gemini (keyword-based analysis only)")
        
        # Template database for fallback
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
        
        # Group clauses by type to avoid duplicates
        clause_groups = {}
        for clause in high_risk + medium_risk:
            clause_type = clause.get('type', 'General Clause')
            if clause_type not in clause_groups:
                clause_groups[clause_type] = []
            clause_groups[clause_type].append(clause)
        
        # Generate one recommendation per clause type with all instances
        for clause_type, clause_list in clause_groups.items():
            # Use the highest risk clause as primary
            primary_clause = clause_list[0]
            priority = 'Critical' if primary_clause.get('risk_level') == 'High' else 'High'
            
            rec = self._create_recommendation(primary_clause, priority, clause_list)
            if rec:
                recommendations.append(rec)
        
        # Sort by priority
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return recommendations
    
    def _create_recommendation(self, clause: Dict, priority: str, all_instances: List[Dict] = None) -> Dict:
        """Create detailed recommendation for a specific clause with actual content analysis"""
        clause_type = clause.get('type', 'General Clause')
        risk_level = clause.get('risk_level', 'Medium')
        clause_text = clause.get('text', '')
        
        # Analyze actual clause content for specific terms
        specific_issues = self._analyze_clause_content(clause_text, clause_type)
        
        # Look up template
        template = self.recommendations_db.get(clause_type, {}).get(risk_level)
        
        if not template:
            # Generate generic recommendation
            template = self._generate_generic_recommendation(clause_type, risk_level)
        
        # Extract key problematic terms from actual text
        key_terms = self._extract_problematic_terms(clause_text, clause_type)
        
        # Count instances
        instance_count = len(all_instances) if all_instances else 1
        instance_note = f" ({instance_count} instances found)" if instance_count > 1 else ""
        
        return {
            'id': clause.get('id'),
            'priority': priority,
            'clause': clause_type + instance_note,
            'clause_snippet': clause_text[:300] if clause_text else 'No text available',
            'full_text': clause_text,
            'issue': specific_issues.get('issue', template.get('issue', 'Requires attention')),
            'recommendation': specific_issues.get('recommendation', template.get('recommendation', 'Negotiate more favorable terms')),
            'negotiation_tips': template.get('tips', []),
            'expected_impact': template.get('impact', 'Improves founder protection'),
            'risk_level': risk_level,
            'specific_concerns': specific_issues.get('concerns', []),
            'detected_terms': key_terms,
            'instances': [{'id': c.get('id'), 'snippet': c.get('text', '')[:150]} for c in (all_instances or [clause])]
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
    
    def _analyze_clause_content(self, text: str, clause_type: str) -> Dict:
        """Analyze actual clause text using AI to identify SPECIFIC issues"""
        if not text or len(text) < 20:
            return {'issue': f"This {clause_type} requires review", 'recommendation': "Consult legal advisor", 'concerns': []}
        
        # Try AI-powered analysis first
        if self.model:
            try:
                prompt = f"""You are an expert startup attorney analyzing a specific clause from a term sheet.

CLAUSE TYPE: {clause_type}
ACTUAL CLAUSE TEXT: "{text}"

Analyze this SPECIFIC clause text and provide:
1. ISSUE: What makes THIS specific clause risky? Quote specific phrases from the text.
2. RECOMMENDATION: Specific negotiation advice for THIS clause (not generic).
3. CONCERNS: List 2-3 specific problems with THIS exact wording.

Be SPECIFIC - reference the actual terms, numbers, and phrases in the clause.
Format as JSON with keys: issue, recommendation, concerns (array)

Example format:
{{
  "issue": "This clause states 'Investors shall have the right to appoint 3 of 5 board members' giving investors 60% control",
  "recommendation": "Negotiate to 2-2-1 board structure: 2 founders, 2 investors, 1 independent director with founder veto on CEO removal",
  "concerns": [
    "Investors can fire founder-CEO with simple majority vote",
    "Founders cannot block strategic decisions like company sale or IP licensing"
  ]
}}"""

                response = self.model.generate_content(prompt)
                result_text = response.text.strip()
                
                # Extract JSON from response
                import json
                if '```json' in result_text:
                    json_str = result_text.split('```json')[1].split('```')[0].strip()
                elif '```' in result_text:
                    json_str = result_text.split('```')[1].split('```')[0].strip()
                else:
                    json_str = result_text
                
                analysis = json.loads(json_str)
                return {
                    'issue': analysis.get('issue', ''),
                    'recommendation': analysis.get('recommendation', ''),
                    'concerns': analysis.get('concerns', [])
                }
            except Exception as e:
                print(f"⚠️  AI analysis failed for {clause_type}: {e}")
                # Fall through to keyword-based analysis
        
        # Fallback: Keyword-based analysis
        text_lower = text.lower() if text else ""
        issues = {'issue': '', 'recommendation': '', 'concerns': []}
        
        if clause_type == "Board Control":
            if 'majority' in text_lower and 'investor' in text_lower:
                issues['issue'] = "Investors have majority board control as stated in this clause"
                issues['recommendation'] = "Negotiate for balanced board: equal founder and investor seats plus independent directors"
                issues['concerns'].append("Founders lose voting power on key decisions")
                issues['concerns'].append("Risk of forced CEO removal")
            elif 'appoint' in text_lower or 'designate' in text_lower:
                issues['issue'] = "Investors can appoint directors without founder approval"
                issues['recommendation'] = "Add requirement for founder consent on board appointments"
                
        elif clause_type == "Liquidation Preference":
            if '3x' in text_lower or '2x' in text_lower:
                multiplier = '3x' if '3x' in text_lower else '2x'
                issues['issue'] = f"Clause specifies {multiplier} liquidation preference - extremely unfavorable"
                issues['recommendation'] = f"Negotiate down to 1x non-participating. {multiplier} will wipe out founder returns in most exits"
                issues['concerns'].append(f"Investors get {multiplier} their investment before founders see anything")
            if 'participating' in text_lower:
                issues['concerns'].append("Participating preference means investors get paid twice")
                
        elif clause_type == "Anti-Dilution":
            if 'full ratchet' in text_lower:
                issues['issue'] = "Full ratchet anti-dilution detected - will cause massive founder dilution"
                issues['recommendation'] = "Must change to broad-based weighted average. Full ratchet is unacceptable"
                issues['concerns'].append("Any down-round will drastically dilute founders")
                issues['concerns'].append("Makes future fundraising nearly impossible")
                
        elif clause_type == "IP Assignment":
            if 'all' in text_lower and ('intellectual property' in text_lower or 'inventions' in text_lower):
                issues['issue'] = "Overly broad IP assignment covering all intellectual property"
                issues['recommendation'] = "Add carve-outs for: (1) prior inventions, (2) side projects, (3) unrelated work"
                issues['concerns'].append("Limits ability to work on other projects")
                issues['concerns'].append("Prior work may be claimed by company")
                
        return issues if issues['issue'] else {'issue': f"This {clause_type} requires review", 'recommendation': "Consult legal advisor", 'concerns': []}
    
    def _extract_problematic_terms(self, text: str, clause_type: str) -> List[str]:
        """Extract specific problematic terms from clause text"""
        terms = []
        
        if not text:
            return terms
            
        text_lower = text.lower()
        
        # Extract multipliers (2x, 3x, etc.)
        multipliers = re.findall(r'\d+x', text_lower)
        terms.extend(multipliers)
        
        # Extract percentages
        percentages = re.findall(r'\d+%', text)
        terms.extend(percentages[:3])  # Limit to first 3
        
        # Extract key phrases
        problematic_phrases = [
            'full ratchet', 'participating', 'majority', 'unilateral',
            'sole discretion', 'at any time', 'without notice', 'all intellectual property'
        ]
        
        for phrase in problematic_phrases:
            if phrase in text_lower:
                terms.append(phrase)
                
        return list(set(terms))[:5]  # Return up to 5 unique terms
