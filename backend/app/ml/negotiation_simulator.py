"""
Negotiation Simulator with AI Investor Role-Play
Trains founders to negotiate better terms through realistic scenarios
"""
import google.generativeai as genai
from typing import Dict, Any, List
import os
from datetime import datetime


class NegotiationSimulator:
    """AI-powered negotiation training system"""
    
    INVESTOR_PROFILES = {
        "aggressive": {
            "name": "Aggressive Investor",
            "description": "Pushes hard on terms, rarely compromises",
            "acceptance_threshold": 0.8,
            "typical_tactics": ["Emphasizes market standard", "Uses time pressure"]
        },
        "balanced": {
            "name": "Balanced Investor",
            "description": "Fair but firm, willing to negotiate",
            "acceptance_threshold": 0.6,
            "typical_tactics": ["References benchmarks", "Willing to compromise"]
        },
        "founder_friendly": {
            "name": "Founder-Friendly Investor",
            "description": "Experienced, values founder success",
            "acceptance_threshold": 0.4,
            "typical_tactics": ["Emphasizes partnership", "Flexible on terms"]
        }
    }
    
    def __init__(self):
        """Initialize negotiation simulator"""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Use same stable model as chat assistant (not experimental)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.ai_enabled = True
                print("✅ Negotiation Simulator: Gemini AI enabled")
            except Exception as e:
                self.ai_enabled = False
                print(f"⚠️ Gemini API failed in negotiation simulator: {str(e)}")
                print("   Using rule-based negotiation")
        else:
            self.ai_enabled = False
            print("⚠️ No Gemini API key - using rule-based negotiation")
    
    def start_negotiation(
        self,
        clause: Dict[str, Any],
        investor_profile: str = "balanced",
        funding_stage: str = "Series A",
        startup_type: str = "SaaS"
    ) -> Dict[str, Any]:
        """Start a new negotiation session"""
        if investor_profile not in self.INVESTOR_PROFILES:
            investor_profile = "balanced"
        
        profile = self.INVESTOR_PROFILES[investor_profile]
        opening = self._generate_opening(clause, profile, funding_stage)
        
        return {
            "session_id": f"neg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "clause": clause,
            "investor_profile": investor_profile,
            "funding_stage": funding_stage,
            "startup_type": startup_type,
            "current_round": 1,
            "max_rounds": 5,
            "status": "in_progress",
            "history": [opening],
            "success_probability": 0.5
        }
    
    def make_counter_offer(
        self,
        session: Dict[str, Any],
        founder_proposal: str,
        reasoning: str = ""
    ) -> Dict[str, Any]:
        """Founder makes a counter-offer"""
        session["current_round"] += 1
        
        # Record founder's move
        founder_move = {
            "round": session["current_round"],
            "actor": "founder",
            "proposal": founder_proposal,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Analyze move quality
        analysis = self._analyze_move(founder_proposal, reasoning)
        founder_move["analysis"] = analysis
        session["history"].append(founder_move)
        
        # Check if should end
        if session["current_round"] >= session["max_rounds"]:
            return self._conclude_negotiation(session, "max_rounds_reached")
        
        # Generate investor response
        response = self._generate_response(session, founder_proposal, analysis)
        session["history"].append(response)
        session["success_probability"] = response.get("acceptance_probability", 0.5)
        
        if response.get("decision") == "accept":
            return self._conclude_negotiation(session, "accepted")
        if response.get("decision") == "reject":
            return self._conclude_negotiation(session, "rejected")
        
        return session
    
    def _generate_opening(self, clause, profile, stage):
        """Generate investor opening position - unique for each profile"""
        clause_type = clause.get('type') or clause.get('clause_type', 'Unknown Clause')
        clause_text = clause.get('text') or clause.get('clause_text', '')
        risk_level = clause.get('risk_level', 'Medium')
        profile_name = profile['name']
        
        # Different opening messages based on investor profile
        if "Aggressive" in profile_name:
            text = f"Let's be direct - the {clause_type} clause needs significant revision. These are industry standard terms, non-negotiable. We've seen 50+ deals this quarter and won't accept outlier positions. Time is critical here."
        elif "Founder-Friendly" in profile_name:
            text = f"Thanks for sharing this {clause_type} clause. I understand your position as a founder. We're flexible and want to find terms that work for everyone. Let's discuss how we can align our interests here."
        else:  # Balanced
            text = f"Regarding the {clause_type} clause - I've reviewed it carefully. While I appreciate your perspective, we need to find middle ground based on market benchmarks. Let's work together on this."
        
        # Add AI enhancement if available
        if self.ai_enabled:
            try:
                prompt = f"""You are a {profile_name} investor. Rewrite this opening position to sound more natural while keeping the same tone:
                
"{text}"

Keep it under 60 words, maintain the {profile_name} personality."""
                
                response = self.model.generate_content(prompt)
                text = response.text.strip()
            except Exception as e:
                print(f"⚠️  AI enhancement failed: {e}")
        
        return {
            "round": 1,
            "actor": "investor",
            "proposal": text,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _analyze_move(self, proposal, reasoning):
        """Analyze founder's move quality"""
        score = 50
        text = (proposal + " " + reasoning).lower()
        
        if reasoning and len(reasoning) > 20:
            score += 10
        if "market" in text or "benchmark" in text:
            score += 15
        if "alignment" in text:
            score += 10
        if "fair" in text:
            score -= 5
        if len(proposal) < 30:
            score -= 15
        
        score = max(0, min(100, score))
        
        return {
            "move_quality_score": score,
            "strengths": ["Used data" if "market" in text else "Engaged"],
            "tips": ["Reference market data" if score < 60 else "Strong move"]
        }
    
    def _generate_response(self, session, proposal, analysis):
        """Generate investor response"""
        profile = self.INVESTOR_PROFILES[session["investor_profile"]]
        quality = analysis["move_quality_score"]
        current_round = session["current_round"]
        
        # Calculate acceptance probability
        prob = profile["acceptance_threshold"] + (quality - 50)/100 - current_round*0.05
        prob = max(0, min(1, prob))
        
        # Determine decision
        if prob > 0.8:
            decision = "accept"
        elif prob < 0.2:
            decision = "reject"
        else:
            decision = "counter"
        
        # Generate varied responses based on profile, round, and decision
        text = self._generate_varied_response(session, proposal, decision, quality, current_round)
        
        return {
            "round": current_round,
            "actor": "investor",
            "proposal": text,
            "decision": decision,
            "acceptance_probability": prob,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_varied_response(self, session, proposal, decision, quality, round_num):
        """Generate varied investor responses"""
        profile_name = session["investor_profile"]
        
        # ACCEPT responses
        if decision == "accept":
            accept_messages = {
                "founder_friendly": [
                    "Perfect! I'm glad we could reach an agreement that works for both sides.",
                    "That's a fair proposal. Let's move forward with these terms.",
                    "I appreciate your flexibility. This structure protects everyone's interests well."
                ],
                "balanced": [
                    "That's reasonable. We can work with those terms.",
                    "Good compromise. Let's finalize this and move forward.",
                    "I can agree to that. This is a fair middle ground."
                ],
                "aggressive": [
                    "Fine. We can accept that, but this is our final position.",
                    "Acceptable. Let's document these terms and close.",
                    "We can live with that. Let's move quickly now."
                ]
            }
            return accept_messages.get(profile_name, ["We can work with that."])[min(round_num-1, 2)]
        
        # REJECT responses
        elif decision == "reject":
            reject_messages = {
                "founder_friendly": [
                    "I understand where you're coming from, but this doesn't work for our fund economics. Let's revisit this clause.",
                    "That's too far from our position. Can we explore other options?",
                    "Unfortunately, that won't meet our investment criteria. We may need to pass."
                ],
                "balanced": [
                    "That proposal doesn't align with market standards. We'll have to reconsider.",
                    "I appreciate the effort, but we can't accept those terms. Perhaps we're not aligned on this deal.",
                    "This won't work for us. We might need to look at other opportunities."
                ],
                "aggressive": [
                    "That's a non-starter. We're not moving on this.",
                    "Unacceptable. We have other deals to focus on if we can't agree.",
                    "This is wasting time. We need to see serious movement or we walk."
                ]
            }
            return reject_messages.get(profile_name, ["This won't work for us."])[min(round_num-1, 2)]
        
        # COUNTER responses (varied by round and profile)
        else:
            if quality >= 70:
                strength = "strong"
            elif quality >= 50:
                strength = "moderate"
            else:
                strength = "weak"
            
            counter_messages = {
                "founder_friendly": {
                    "strong": [
                        "That's a strong proposal. Let me suggest a small adjustment that could work for both of us.",
                        "I like where you're going with this. How about we add a provision that protects both sides?",
                        "You're on the right track. Let's refine this a bit more to make it bulletproof."
                    ],
                    "moderate": [
                        "I see your point. Can we find a middle ground that addresses both our concerns?",
                        "That's progress. Let me propose an alternative that might work better.",
                        "We're getting closer. What if we structured it slightly differently?"
                    ],
                    "weak": [
                        "I appreciate the effort, but we need to strengthen this proposal with more specifics.",
                        "Let's dig deeper here. Can you provide more reasoning for this approach?",
                        "We need to bridge the gap a bit more. What else can we adjust?"
                    ]
                },
                "balanced": {
                    "strong": [
                        "That's closer to market terms. I'd like to propose one modification based on industry standards.",
                        "Good reasoning. Let me counter with terms that are more aligned with recent deals.",
                        "I appreciate the data. Here's how we typically structure this in comparable situations."
                    ],
                    "moderate": [
                        "That's a step in the right direction. However, we need to adjust based on our portfolio requirements.",
                        "I see merit in your approach, but let me propose a variation that works better for us.",
                        "We're narrowing the gap. Let me suggest terms that balance both our needs."
                    ],
                    "weak": [
                        "That's still far from standard market terms. We need to see more movement.",
                        "You'll need to provide stronger justification or come closer to benchmarks.",
                        "This doesn't align with comparable deals. Let's recalibrate our positions."
                    ]
                },
                "aggressive": {
                    "strong": [
                        "You're being more realistic now. But we still need better terms than that.",
                        "Closer, but not quite there. Here's our counter: take it or leave it.",
                        "That's more like it. Now let's finalize with terms that actually work for us."
                    ],
                    "moderate": [
                        "Not enough movement. We need significant changes or this won't close.",
                        "You're still not in the ballpark. Time to make a real decision here.",
                        "This is taking too long. Either meet our requirements or we move on."
                    ],
                    "weak": [
                        "That's not going to cut it. We're running out of patience here.",
                        "Unacceptable. You need to come back with serious terms or we're done.",
                        "Stop wasting our time. Either match market standards or this conversation ends."
                    ]
                }
            }
            
            messages = counter_messages.get(profile_name, {}).get(strength, ["That's closer, but let me propose a middle ground."])
            return messages[min(round_num-1, len(messages)-1)]
    
    def _conclude_negotiation(self, session, outcome):
        """Conclude negotiation"""
        session["status"] = "completed"
        session["outcome"] = outcome
        
        if outcome == "accepted":
            session["final_score"] = 100
        elif outcome == "rejected":
            session["final_score"] = 0
        else:
            session["final_score"] = int(session["success_probability"] * 100)
        
        # Generate lessons
        session["lessons"] = [{
            "category": "Performance",
            "lesson": f"Negotiation {outcome}",
            "details": f"Final score: {session['final_score']}"
        }]
        
        return session
