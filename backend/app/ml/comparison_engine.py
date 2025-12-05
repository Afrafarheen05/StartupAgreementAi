"""
Multi-Document Comparison Engine
Compares multiple agreements side-by-side with AI-powered recommendations
"""
import google.generativeai as genai
from typing import List, Dict, Any
import os
from datetime import datetime


class ComparisonEngine:
    """Intelligent comparison of multiple agreements"""
    
    def __init__(self):
        """Initialize comparison engine with Gemini AI"""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.ai_enabled = True
        else:
            self.ai_enabled = False
            print("⚠️ No Gemini API key - using rule-based comparison")
    
    def compare_documents(
        self,
        documents: List[Dict[str, Any]],
        comparison_name: str = "Document Comparison"
    ) -> Dict[str, Any]:
        """
        Compare multiple documents and determine the best one
        
        Args:
            documents: List of analyzed document dictionaries
            comparison_name: Name for this comparison
            
        Returns:
            Comprehensive comparison results
        """
        if len(documents) < 2:
            raise ValueError("Need at least 2 documents to compare")
        
        print(f"🔍 Comparing {len(documents)} documents...")
        
        # Extract key metrics for comparison
        comparison_data = []
        for idx, doc in enumerate(documents, 1):
            # Properly extract risk assessment data
            risk_assessment = doc.get("risk_assessment", {})
            clauses = doc.get("clauses", [])
            
            comparison_data.append({
                "document_id": idx,
                "filename": doc.get("filename", f"Document {idx}"),
                "overall_risk_score": risk_assessment.get("overall_score", 0),
                "risk_level": risk_assessment.get("overall_level", "Unknown"),
                "total_clauses": len(clauses),
                "high_risk_count": sum(1 for c in clauses if c.get("risk_level") == "High"),
                "critical_risk_count": sum(1 for c in clauses if c.get("risk_level") == "Critical"),
                "clauses": clauses,
                "red_flags": risk_assessment.get("red_flags", 0),
                "dangerous_clauses": risk_assessment.get("dangerous_clauses", [])
            })
        
        # Perform clause-by-clause comparison
        clause_comparison = self._compare_clauses(comparison_data)
        
        # Calculate winner
        winner = self._determine_winner(comparison_data)
        
        # Generate financial impact analysis
        financial_impact = self._calculate_financial_impact(comparison_data)
        
        # AI-powered insights (if available)
        ai_insights = None
        if self.ai_enabled:
            ai_insights = self._generate_ai_insights(comparison_data, clause_comparison)
        
        return {
            "comparison_name": comparison_name,
            "timestamp": datetime.utcnow().isoformat(),
            "documents": comparison_data,
            "winner": winner,
            "clause_comparison": clause_comparison,
            "financial_impact": financial_impact,
            "ai_insights": ai_insights,
            "summary": self._generate_summary(comparison_data, winner, financial_impact)
        }
    
    def _compare_clauses(self, comparison_data: List[Dict]) -> Dict[str, Any]:
        """Compare clauses across documents"""
        clause_types = set()
        for doc in comparison_data:
            for clause in doc["clauses"]:
                clause_types.add(clause.get("type", "Unknown"))
        
        clause_winners = {}
        for clause_type in clause_types:
            clause_details = []
            for doc in comparison_data:
                matching_clauses = [
                    c for c in doc["clauses"]
                    if c.get("type") == clause_type
                ]
                if matching_clauses:
                    # Map risk levels to numeric scores
                    risk_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4, "Unknown": 5}
                    risk_level = matching_clauses[0].get("risk_level", "Unknown")
                    clause_details.append({
                        "document_id": doc["document_id"],
                        "risk_score": risk_map.get(risk_level, 5),
                        "risk_level": risk_level,
                        "text": matching_clauses[0].get("text", "")[:200]
                    })
            
            # Determine best clause version (lowest risk)
            if clause_details:
                best = min(clause_details, key=lambda x: x["risk_score"])
                clause_winners[clause_type] = {
                    "winner_document": best["document_id"],
                    "winner_risk_score": best["risk_score"],
                    "all_versions": clause_details
                }
        
        return clause_winners
    
    def _determine_winner(self, comparison_data: List[Dict]) -> Dict[str, Any]:
        """Determine which document is best overall"""
        # Scoring system
        scores = []
        for doc in comparison_data:
            # Lower risk is better
            risk_penalty = doc["overall_risk_score"] * 10
            
            # Fewer high-risk clauses is better
            high_risk_penalty = doc["high_risk_count"] * 5
            critical_risk_penalty = doc["critical_risk_count"] * 15
            
            # Calculate total score (lower is better)
            total_score = risk_penalty + high_risk_penalty + critical_risk_penalty
            
            scores.append({
                "document_id": doc["document_id"],
                "filename": doc["filename"],
                "total_score": total_score,
                "breakdown": {
                    "risk_penalty": risk_penalty,
                    "high_risk_penalty": high_risk_penalty,
                    "critical_risk_penalty": critical_risk_penalty
                }
            })
        
        # Winner has lowest score
        winner = min(scores, key=lambda x: x["total_score"])
        
        return {
            "winner_document_id": winner["document_id"],
            "winner_filename": winner["filename"],
            "winner_score": winner["total_score"],
            "all_scores": scores,
            "confidence": self._calculate_confidence(scores)
        }
    
    def _calculate_confidence(self, scores: List[Dict]) -> float:
        """Calculate how confident we are in the winner - improved algorithm"""
        sorted_scores = sorted(scores, key=lambda x: x["total_score"])
        if len(sorted_scores) < 2:
            return 0.95  # High confidence if only one document
        
        best = sorted_scores[0]["total_score"]
        second_best = sorted_scores[1]["total_score"]
        
        # If both scores are 0 or very close, lower confidence
        if best == 0 and second_best == 0:
            return 0.60
        
        if second_best == 0:
            return 0.92  # High confidence if winner is clearly better
        
        # Calculate percentage difference
        difference_pct = abs(best - second_best) / max(second_best, 1)
        
        # Map difference to confidence:
        # 0-10% difference -> 60-70% confidence (close call)
        # 10-30% difference -> 70-85% confidence (clear winner)
        # 30%+ difference -> 85-95% confidence (obvious winner)
        if difference_pct < 0.1:
            confidence = 0.60 + (difference_pct / 0.1) * 0.10  # 60-70%
        elif difference_pct < 0.3:
            confidence = 0.70 + ((difference_pct - 0.1) / 0.2) * 0.15  # 70-85%
        else:
            confidence = min(0.85 + ((difference_pct - 0.3) * 0.1), 0.95)  # 85-95%
        
        return round(confidence, 2)
    
    def _calculate_financial_impact(self, comparison_data: List[Dict]) -> Dict[str, Any]:
        """Estimate financial impact of choosing each agreement"""
        impacts = []
        
        # Assumed startup valuation for calculations
        ASSUMED_VALUATION = 10_000_000  # $10M
        
        for doc in comparison_data:
            # Calculate impact based on overall risk score
            risk_score = doc["overall_risk_score"]
            
            # Higher risk = more equity loss and exit reduction
            # Risk score 0-100 maps to 0-30% equity dilution and 0-50% exit reduction
            equity_loss_pct = (risk_score / 100) * 30  # Max 30% additional dilution
            exit_reduction_pct = (risk_score / 100) * 50  # Max 50% exit value reduction
            
            equity_loss_dollars = ASSUMED_VALUATION * (equity_loss_pct / 100)
            exit_reduction_dollars = ASSUMED_VALUATION * (exit_reduction_pct / 100)
            
            impacts.append({
                "document_id": doc["document_id"],
                "filename": doc["filename"],
                "estimated_equity_loss": round(equity_loss_pct, 1),
                "estimated_exit_reduction": round(exit_reduction_pct, 1),
                "equity_loss_dollars": round(equity_loss_dollars, 0),
                "exit_reduction_dollars": round(exit_reduction_dollars, 0),
                "total_financial_risk": round(equity_loss_dollars + exit_reduction_dollars, 0)
            })
        
        # Find best and worst deals
        best_deal = min(impacts, key=lambda x: x["total_financial_risk"])
        worst_deal = max(impacts, key=lambda x: x["total_financial_risk"])
        
        # Calculate differences from best deal
        for impact in impacts:
            impact["vs_best_deal"] = round(
                impact["total_financial_risk"] - best_deal["total_financial_risk"],
                0
            )
        
        return {
            "impacts": impacts,
            "best_case": int(best_deal["total_financial_risk"]),
            "worst_case": int(worst_deal["total_financial_risk"]),
            "best_financial_deal": best_deal["document_id"],
            "worst_financial_deal": worst_deal["document_id"],
            "explanation": f"Based on risk analysis, choosing the best agreement could save you ${int((worst_deal['total_financial_risk'] - best_deal['total_financial_risk'])/1000000)}M+ in equity preservation and exit value."
        }
    
    def _generate_ai_insights(
        self,
        comparison_data: List[Dict],
        clause_comparison: Dict
    ) -> str:
        """Generate AI-powered insights using Gemini"""
        try:
            # Prepare prompt
            prompt = f"""You are an expert startup lawyer comparing term sheets for a founder.

DOCUMENTS TO COMPARE:
{self._format_comparison_for_ai(comparison_data, clause_comparison)}

Provide a concise analysis in 3-4 bullet points:
1. Which document is best overall and why
2. Key differences that matter most financially
3. Specific negotiation opportunities
4. Red flags to watch out for

Be specific and actionable. Focus on financial impact."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"AI insights error: {e}")
            return None
    
    def _format_comparison_for_ai(
        self,
        comparison_data: List[Dict],
        clause_comparison: Dict
    ) -> str:
        """Format comparison data for AI analysis"""
        output = []
        
        for doc in comparison_data:
            output.append(f"\n{'='*50}")
            output.append(f"DOCUMENT {doc['document_id']}: {doc['filename']}")
            output.append(f"{'='*50}")
            output.append(f"Overall Risk Score: {doc['overall_risk_score']:.2f}")
            output.append(f"Risk Level: {doc['risk_level']}")
            output.append(f"Total Clauses: {doc['total_clauses']}")
            output.append(f"High Risk: {doc['high_risk_count']}, Critical: {doc['critical_risk_count']}")
            
            # Key clauses
            output.append("\nKEY CLAUSES:")
            high_risk_clauses = [
                c for c in doc["clauses"]
                if c.get("risk_level") in ["high", "critical"]
            ][:3]
            
            for clause in high_risk_clauses:
                output.append(f"  • {clause.get('clause_type')}: {clause.get('risk_level')} risk")
                output.append(f"    Text: {clause.get('clause_text', '')[:150]}...")
        
        return "\n".join(output)
    
    def _generate_summary(
        self,
        comparison_data: List[Dict],
        winner: Dict,
        financial_impact: Dict
    ) -> str:
        """Generate human-readable summary"""
        winner_doc = next(
            d for d in comparison_data
            if d["document_id"] == winner["winner_document_id"]
        )
        
        summary_lines = [
            f"📊 **COMPARISON SUMMARY**",
            f"",
            f"🏆 **Winner**: Document {winner['winner_document_id']} - {winner['winner_filename']}",
            f"",
            f"**Why it's the best:**",
            f"  • Overall Risk Score: {winner_doc['overall_risk_score']:.2f} ({winner_doc['risk_level']})",
            f"  • High Risk Clauses: {winner_doc['high_risk_count']}",
            f"  • Critical Risk Clauses: {winner_doc['critical_risk_count']}",
            f"  • Confidence: {winner['confidence'] * 100:.0f}%",
            f"",
            f"💰 **Financial Impact:**"
        ]
        
        winner_impact = next(
            i for i in financial_impact["impacts"]
            if i["document_id"] == winner["winner_document_id"]
        )
        
        summary_lines.append(
            f"  • Estimated Equity Loss: {winner_impact['estimated_equity_loss']}%"
        )
        summary_lines.append(
            f"  • Estimated Exit Reduction: {winner_impact['estimated_exit_reduction']}%"
        )
        
        # Show how much worse other deals are
        other_docs = [
            d for d in comparison_data
            if d["document_id"] != winner["winner_document_id"]
        ]
        
        if other_docs:
            summary_lines.append(f"")
            summary_lines.append(f"⚠️ **Other Documents:**")
            for doc in other_docs:
                doc_impact = next(
                    i for i in financial_impact["impacts"]
                    if i["document_id"] == doc["document_id"]
                )
                summary_lines.append(
                    f"  • Document {doc['document_id']}: "
                    f"{doc_impact['vs_best_deal']:.1f}% more financial risk"
                )
        
        return "\n".join(summary_lines)
