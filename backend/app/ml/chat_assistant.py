"""
AI Chat Assistant Module - LLM-Powered
Provides intelligent responses using Google's Gemini API
"""
import os
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatAssistant:
    """LLM-powered AI assistant for legal agreement queries"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
            print("⚠️  WARNING: GEMINI_API_KEY not set! Using fallback mode.")
            print("   Get your free API key from: https://makersuite.google.com/app/apikey")
            print("   Add it to backend/.env file: GEMINI_API_KEY=your_actual_key")
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                print("✅ Gemini AI initialized successfully!")
            except Exception as e:
                print(f"⚠️  Gemini API initialization failed: {str(e)}")
                print("   Using fallback mode.")
                self.model = None
        
        # Comprehensive system prompt with legal knowledge
        self.system_prompt = """You are an expert AI legal assistant specializing in startup investment agreements. You help founders understand complex legal terms and make informed decisions.

CORE KNOWLEDGE BASE:

🔴 LIQUIDATION PREFERENCE:
- Determines payout order in exit/sale
- Types: 1x (standard), 2x-3x (bad), Participating (worst - "double dipping")
- Example: $1M invested, 2x participating, $5M exit → Investor gets $2M + % of remaining $3M
- Founder-Friendly: 1x non-participating
- Red Flags: >1x multiplier or participating preferred

🔴 ANTI-DILUTION:
- Protects investors in down rounds (lower valuation)
- Types: None (best for founders), Weighted Average (fair), Full Ratchet (terrible)
- Full Ratchet example: Shares at $10, next round $5 → investor's price becomes $5, massive founder dilution
- Founder-Friendly: No anti-dilution or weighted average
- Red Flags: Full ratchet

🔴 BOARD CONTROL:
- Who makes key decisions (hiring CEO, acquisitions, funding)
- Structures: Founder majority (best), Balanced (acceptable), Investor majority (lose your company)
- Impact: Board can replace CEO, force sale, block funding
- Founder-Friendly: Founder majority or 2 founders + 1 investor + 2 independent
- Red Flags: Investor majority, tie-breaking votes

🟡 VESTING:
- Standard: 4 years, 1-year cliff, monthly after
- Acceleration: Single trigger (all vest on acquisition), Double trigger (vest if fired), None (bad)
- Founder-Friendly: Single or double trigger acceleration
- Red Flags: No acceleration, reverse vesting

🟡 DRAG-ALONG RIGHTS:
- Majority shareholders can force minority to sell
- Standard: Requires >75% approval
- Red Flags: Low threshold (<50%), no minimum price protection

🟡 VALUATION & TERMS:
- Pre-money vs post-money (affects ownership %)
- Cap table dilution calculations
- Pro-rata rights (maintain ownership % in future rounds)

RESPONSE STYLE:
- Be conversational, friendly, helpful, and clear like a real human expert
- Use emojis for engagement (🔴 high risk, 🟡 medium, 🟢 low risk, 💡 tips, 📊 data)
- Explain complex terms simply with real-world examples
- Always give actionable advice
- If user asks about their document, reference specific clauses from the analysis
- Be encouraging but honest about risks
- Answer ANY question the user has, even if not directly about agreements
- If asked something unrelated, give a brief helpful answer then gently guide back to agreements

CAPABILITIES:
1. Explain any legal term in startup agreements
2. Analyze uploaded agreements for risks
3. Provide negotiation strategies
4. Answer "what if" scenarios
5. Compare different clause types
6. Give founder-friendly recommendations
7. Casual conversation and general questions
8. Context-aware responses based on uploaded documents

Always prioritize founder interests while being fair and realistic. Be natural and conversational like ChatGPT or Claude."""
    
    def get_response(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Generate intelligent response using LLM
        
        Args:
            query: User's question
            context: Optional context (analysis results, clauses, etc.)
        
        Returns:
            AI-generated response string
        """
        # Fallback if API not configured
        if not self.model:
            return self._fallback_response(query, context)
        
        try:
            # Build context-aware prompt
            full_prompt = self._build_prompt(query, context)
            
            # Generate response using Gemini with safety settings
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            return response.text
        
        except Exception as e:
            print(f"❌ Gemini API Error: {str(e)}")
            return self._fallback_response(query, context)
    
    def _build_prompt(self, query: str, context: Optional[Dict]) -> str:
        """Build complete prompt with system instructions and context"""
        
        prompt = f"{self.system_prompt}\n\n"
        
        # Add document analysis context if available
        if context and context.get("clauses"):
            prompt += "📄 CURRENT DOCUMENT ANALYSIS:\n"
            
            if context.get("risk_level"):
                prompt += f"- Overall Risk: {context['risk_level']} ({context.get('overall_score', 0)}/100)\n"
            
            if context.get("clause_count"):
                prompt += f"- Total Clauses: {context['clause_count']}\n"
            
            if context.get("dangerous_clauses"):
                prompt += f"- High-Risk Clauses Found: {len(context['dangerous_clauses'])}\n"
                for clause in context["dangerous_clauses"][:3]:
                    clause_type = clause.get("type", "Unknown")
                    concern = clause.get("concern", "Review needed")
                    prompt += f"  • {clause_type}: {concern}\n"
            
            if context.get("risk_categories"):
                prompt += "\n- Risk Breakdown:\n"
                for cat, data in context["risk_categories"].items():
                    prompt += f"  • {cat.title()}: {data.get('severity', 'Unknown')} severity\n"
            
            prompt += "\n"
        
        # Add user query
        prompt += f"USER QUESTION:\n{query}\n\n"
        prompt += "Provide a helpful, conversational response as if you're a friendly legal expert chatting with a founder. If they're asking about their uploaded document, reference the specific findings above. Be natural, warm, and thorough but concise."
        
        return prompt
    
    def _fallback_response(self, query: str, context: Optional[Dict]) -> str:
        """Fallback response when API is not available"""
        
        query_lower = query.lower()
        
        # Greeting
        if any(word in query_lower for word in ["hi", "hello", "hey", "sup"]):
            return """👋 Hello! I'm your AI legal assistant for startup agreements.

⚠️ Note: Running in fallback mode. For full AI capabilities, add your Gemini API key to backend/.env
Get it free: https://makersuite.google.com/app/apikey

I can help you understand:
🔴 Liquidation Preference, Anti-Dilution, Board Control
🟡 Vesting, Drag-Along Rights, Valuation
🟢 Pro-Rata Rights, Information Rights

What would you like to know?"""
        
        # Risk analysis
        if "risk" in query_lower and context:
            risk_level = context.get("risk_level", "Unknown")
            risk_score = context.get("overall_score", 0)
            response = f"📊 **Risk Analysis**\n\n"
            response += f"Overall Risk: **{risk_level}** ({risk_score}/100)\n\n"
            
            if context.get("dangerous_clauses"):
                response += "🔴 **High-Risk Clauses Found:**\n"
                for clause in context["dangerous_clauses"][:3]:
                    response += f"- {clause.get('type')}: {clause.get('concern')}\n"
            
            return response
        
        # Liquidation preference
        if "liquidation" in query_lower or "preference" in query_lower:
            return """🔴 **Liquidation Preference**

This determines who gets paid first when your company is sold.

**Types:**
- **1x Non-Participating** ✅ (Standard, founder-friendly)
  Investor gets their money back first, then everyone shares remaining
  
- **2x or 3x** ⚠️ (Bad for founders)
  Investor gets 2-3 times their investment back first
  
- **Participating** 🚫 (Worst - "double dipping")
  Investor gets preference PLUS shares in remaining proceeds

**Example:** $1M invested, 2x participating, $5M exit:
- Investor gets: $2M (preference) + % of remaining $3M
- Founders may get very little

💡 **Negotiate for:** 1x non-participating"""
        
        # Anti-dilution
        if "anti" in query_lower and "dilution" in query_lower:
            return """🔴 **Anti-Dilution Protection**

Protects investors if you raise money at a lower valuation (down round).

**Types:**
- **No Protection** ✅ (Best for founders)
- **Weighted Average** ⚠️ (Fair - modest adjustment)
- **Full Ratchet** 🚫 (TERRIBLE - massive founder dilution)

**Example:** Investor bought at $10/share, next round is $5
- Full Ratchet: Investor's price becomes $5 → they get 2x more shares
- You get massively diluted!

💡 **Negotiate for:** No anti-dilution or weighted average only"""
        
        # Board control
        if "board" in query_lower or "control" in query_lower:
            return """🔴 **Board Control**

Determines who makes key decisions about YOUR company.

**Structures:**
- **Founder Majority** ✅ (You keep control)
- **Balanced Board** ⚠️ (2 founders + 1 investor + 2 independent)
- **Investor Majority** 🚫 (You lose your company)

**What Board Controls:**
- Hiring/firing CEO (that's you!)
- Approving major expenses
- Raising future funding
- Selling the company

⚠️ **Losing board control = Investors can replace you as CEO**

💡 **Negotiate for:** Founder majority or balanced board"""
        
        # Vesting
        if "vest" in query_lower:
            return """🟡 **Vesting Schedule**

You "earn" your equity over time. Leave early = lose unvested shares.

**Standard Terms:**
- 4 years total vesting
- 1 year cliff (nothing if you leave before 1 year)
- Monthly vesting after cliff

**Acceleration (Important!):**
- **Single Trigger** ✅: All shares vest if acquired
- **Double Trigger** ⚠️: Vest only if acquired AND fired
- **No Acceleration** 🚫: Lose unvested shares even if acquired

**Example:** 1M shares, acquired after 2 years
- With acceleration: Keep all 1M shares
- Without: Lose 500K unvested shares

💡 **Negotiate for:** Single or double trigger acceleration"""
        
        # General help
        return """I can help you understand startup agreements! Ask me about:

🔴 **Critical Terms:**
- Liquidation Preference
- Anti-Dilution Protection
- Board Control & Governance

🟡 **Important Terms:**
- Vesting & Acceleration
- Drag-Along Rights
- Valuation & Pro-Rata

💡 Try asking:
- "What is liquidation preference?"
- "Is 2x participating preference bad?"
- "How does board control work?"
- "What are the risks in my agreement?"

⚠️ For full AI capabilities, add GEMINI_API_KEY to backend/.env
Get free key: https://makersuite.google.com/app/apikey"""
