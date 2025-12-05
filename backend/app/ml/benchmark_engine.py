"""
Market Benchmark Database & Intelligence Engine
Compare agreement terms against industry standards and market data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics


class BenchmarkEngine:
    """Market intelligence and benchmarking for agreement terms"""
    
    # Industry benchmark database (would be loaded from DB in production)
    BENCHMARK_DATA = {
        "Liquidation Preference": {
            "SaaS": {
                "Pre-seed": {"p25": 1.0, "median": 1.0, "p75": 1.0, "frequency": 95},
                "Seed": {"p25": 1.0, "median": 1.0, "p75": 1.5, "frequency": 98},
                "Series A": {"p25": 1.0, "median": 1.0, "p75": 1.5, "frequency": 100},
                "Series B": {"p25": 1.0, "median": 1.5, "p75": 2.0, "frequency": 100}
            },
            "Fintech": {
                "Seed": {"p25": 1.0, "median": 1.5, "p75": 2.0, "frequency": 98},
                "Series A": {"p25": 1.0, "median": 1.5, "p75": 2.0, "frequency": 100}
            },
            "Biotech": {
                "Seed": {"p25": 1.5, "median": 2.0, "p75": 2.5, "frequency": 100},
                "Series A": {"p25": 1.5, "median": 2.0, "p75": 3.0, "frequency": 100}
            }
        },
        "Board Seats": {
            "SaaS": {
                "Seed": {"p25": 1, "median": 1, "p75": 2, "frequency": 85},
                "Series A": {"p25": 1, "median": 2, "p75": 2, "frequency": 95},
                "Series B": {"p25": 2, "median": 2, "p75": 3, "frequency": 98}
            }
        },
        "Valuation Cap": {
            "SaaS": {
                "Pre-seed": {"p25": 5000000, "median": 8000000, "p75": 12000000, "frequency": 90},
                "Seed": {"p25": 8000000, "median": 12000000, "p75": 20000000, "frequency": 85}
            }
        },
        "Founder Vesting": {
            "SaaS": {
                "All Stages": {"p25": 36, "median": 48, "p75": 48, "frequency": 92}
            }
        },
        "Pro-Rata Rights": {
            "SaaS": {
                "Seed": {"frequency": 75, "threshold": 500000},
                "Series A": {"frequency": 90, "threshold": 1000000}
            }
        }
    }
    
    def __init__(self):
        """Initialize benchmark engine"""
        print("✅ Benchmark Engine initialized with market data")
    
    def benchmark_clause(
        self,
        clause_type: str,
        clause_value: Any,
        startup_type: str = "SaaS",
        funding_stage: str = "Series A"
    ) -> Dict[str, Any]:
        """
        Benchmark a clause against market standards
        
        Args:
            clause_type: Type of clause (e.g., "Liquidation Preference")
            clause_value: Actual value in the agreement
            startup_type: Industry/type of startup
            funding_stage: Funding stage
            
        Returns:
            Benchmarking analysis
        """
        if clause_type not in self.BENCHMARK_DATA:
            return {
                "clause_type": clause_type,
                "status": "no_benchmark_data",
                "message": f"No benchmark data available for {clause_type}"
            }
        
        industry_data = self.BENCHMARK_DATA[clause_type].get(startup_type, {})
        if not industry_data:
            startup_type = "SaaS"  # Fallback to SaaS
            industry_data = self.BENCHMARK_DATA[clause_type].get(startup_type, {})
        
        stage_data = industry_data.get(funding_stage) or industry_data.get("All Stages")
        if not stage_data:
            return {
                "clause_type": clause_type,
                "status": "no_stage_data",
                "message": f"No data for {funding_stage} stage"
            }
        
        # Calculate percentile
        percentile = self._calculate_percentile(clause_value, stage_data)
        
        # Determine if founder-friendly
        is_founder_friendly = percentile <= 50  # Lower is better for founders
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            clause_type, clause_value, stage_data, percentile
        )
        
        return {
            "clause_type": clause_type,
            "your_value": clause_value,
            "market_data": {
                "25th_percentile": stage_data.get("p25"),
                "median": stage_data.get("median"),
                "75th_percentile": stage_data.get("p75"),
                "frequency": stage_data.get("frequency", 0)
            },
            "your_percentile": percentile,
            "is_standard": 25 <= percentile <= 75,
            "is_founder_friendly": is_founder_friendly,
            "comparison": self._generate_comparison(percentile),
            "recommendations": recommendations
        }
    
    def benchmark_document(
        self,
        clauses: List[Dict[str, Any]],
        startup_type: str = "SaaS",
        funding_stage: str = "Series A"
    ) -> Dict[str, Any]:
        """
        Benchmark entire document against market
        
        Args:
            clauses: List of extracted clauses
            startup_type: Industry
            funding_stage: Stage
            
        Returns:
            Comprehensive benchmarking report
        """
        benchmarked_clauses = []
        total_score = 0
        founder_friendly_count = 0
        
        for clause in clauses:
            clause_type = clause.get("clause_type")
            
            # Extract value from clause (simplified - would use NLP in production)
            clause_value = self._extract_value_from_clause(clause)
            
            if clause_value is not None:
                benchmark = self.benchmark_clause(
                    clause_type, clause_value, startup_type, funding_stage
                )
                
                benchmarked_clauses.append(benchmark)
                
                if benchmark.get("is_founder_friendly"):
                    founder_friendly_count += 1
                
                # Score based on percentile (closer to 25th percentile is better)
                if benchmark.get("your_percentile"):
                    total_score += (100 - abs(benchmark["your_percentile"] - 25))
        
        # Calculate overall score
        overall_score = total_score / len(benchmarked_clauses) if benchmarked_clauses else 0
        
        # Generate market intelligence
        market_intelligence = self._generate_market_intelligence(
            benchmarked_clauses, startup_type, funding_stage
        )
        
        return {
            "startup_type": startup_type,
            "funding_stage": funding_stage,
            "benchmarked_clauses": benchmarked_clauses,
            "summary": {
                "total_clauses_benchmarked": len(benchmarked_clauses),
                "founder_friendly_clauses": founder_friendly_count,
                "overall_market_score": round(overall_score, 1),
                "rating": self._get_rating(overall_score)
            },
            "market_intelligence": market_intelligence,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def compare_to_market(
        self,
        your_terms: Dict[str, Any],
        startup_type: str = "SaaS",
        funding_stage: str = "Series A"
    ) -> Dict[str, Any]:
        """
        Compare your specific terms to market averages
        
        Args:
            your_terms: Dict of {clause_type: value}
            startup_type: Industry
            funding_stage: Stage
            
        Returns:
            Detailed comparison
        """
        comparisons = []
        
        for clause_type, your_value in your_terms.items():
            benchmark = self.benchmark_clause(
                clause_type, your_value, startup_type, funding_stage
            )
            
            if benchmark.get("status") != "no_benchmark_data":
                market_median = benchmark["market_data"]["median"]
                
                # Calculate financial impact (simplified)
                impact = self._calculate_financial_impact(
                    clause_type, your_value, market_median
                )
                
                comparisons.append({
                    "clause_type": clause_type,
                    "your_value": your_value,
                    "market_median": market_median,
                    "difference": your_value - market_median if isinstance(your_value, (int, float)) else "N/A",
                    "percentile": benchmark["your_percentile"],
                    "financial_impact": impact,
                    "verdict": benchmark["comparison"]
                })
        
        return {
            "comparisons": comparisons,
            "overall_assessment": self._generate_overall_assessment(comparisons)
        }
    
    def get_industry_trends(
        self,
        startup_type: str = "SaaS",
        funding_stage: str = "Series A"
    ) -> Dict[str, Any]:
        """Get current industry trends and standards"""
        trends = []
        
        for clause_type, data in self.BENCHMARK_DATA.items():
            industry_data = data.get(startup_type, {})
            stage_data = industry_data.get(funding_stage)
            
            if stage_data:
                trend = {
                    "clause_type": clause_type,
                    "market_standard": stage_data.get("median"),
                    "typical_range": {
                        "min": stage_data.get("p25"),
                        "max": stage_data.get("p75")
                    },
                    "frequency": stage_data.get("frequency", 0),
                    "recommendation": self._get_trend_recommendation(clause_type, stage_data)
                }
                trends.append(trend)
        
        return {
            "startup_type": startup_type,
            "funding_stage": funding_stage,
            "trends": trends,
            "key_insights": self._generate_key_insights(trends)
        }
    
    def _calculate_percentile(self, value: Any, stage_data: Dict) -> float:
        """Calculate percentile of value within market data"""
        if not isinstance(value, (int, float)):
            return 50  # Default to median if non-numeric
        
        p25 = stage_data.get("p25", 0)
        median = stage_data.get("median", 0)
        p75 = stage_data.get("p75", 0)
        
        if value <= p25:
            return 25
        elif value <= median:
            # Interpolate between 25th and 50th
            return 25 + ((value - p25) / (median - p25) * 25) if median != p25 else 25
        elif value <= p75:
            # Interpolate between 50th and 75th
            return 50 + ((value - median) / (p75 - median) * 25) if p75 != median else 50
        else:
            return 75 + min((value - p75) / p75 * 25, 25)
    
    def _generate_comparison(self, percentile: float) -> str:
        """Generate human-readable comparison"""
        if percentile <= 25:
            return "Excellent - Better than 75% of deals"
        elif percentile <= 50:
            return "Good - Better than median"
        elif percentile <= 75:
            return "Below Average - Worse than median"
        else:
            return "Poor - Worse than 75% of deals"
    
    def _generate_recommendations(
        self,
        clause_type: str,
        value: Any,
        stage_data: Dict,
        percentile: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if percentile > 75:
            recommendations.append(
                f"Your {clause_type} is in the worst 25% of deals. Strong negotiation recommended."
            )
            recommendations.append(
                f"Market standard is {stage_data.get('median')}. Push for closer to this."
            )
        elif percentile > 50:
            recommendations.append(
                f"You can likely negotiate better terms. Median is {stage_data.get('median')}."
            )
        else:
            recommendations.append(
                f"Your terms are competitive. This is a founder-friendly clause."
            )
        
        return recommendations
    
    def _extract_value_from_clause(self, clause: Dict) -> Optional[Any]:
        """Extract numeric value from clause (simplified)"""
        clause_type = clause.get("clause_type", "").lower()
        text = clause.get("clause_text", "").lower()
        
        # Simple pattern matching (would use NLP in production)
        if "liquidation preference" in clause_type:
            if "2x" in text or "two times" in text:
                return 2.0
            elif "1.5x" in text:
                return 1.5
            else:
                return 1.0
        
        # Default to None if can't extract
        return None
    
    def _calculate_financial_impact(
        self,
        clause_type: str,
        your_value: Any,
        market_median: Any
    ) -> str:
        """Calculate estimated financial impact"""
        if not isinstance(your_value, (int, float)) or not isinstance(market_median, (int, float)):
            return "Unable to calculate"
        
        difference = your_value - market_median
        
        if "Liquidation Preference" in clause_type:
            if difference > 0:
                return f"Could cost {difference * 10:.0f}% of exit value"
            else:
                return "Favorable terms"
        
        if "Valuation Cap" in clause_type:
            percentage = (difference / market_median * 100) if market_median else 0
            if difference < 0:
                return f"{abs(percentage):.0f}% below market (more dilution)"
            else:
                return f"{percentage:.0f}% above market (less dilution)"
        
        return "Impact varies by exit scenario"
    
    def _generate_market_intelligence(
        self,
        benchmarked_clauses: List[Dict],
        startup_type: str,
        funding_stage: str
    ) -> Dict[str, Any]:
        """Generate market intelligence insights"""
        insights = []
        
        # Count favorable vs unfavorable clauses
        favorable = sum(1 for c in benchmarked_clauses if c.get("is_founder_friendly"))
        unfavorable = len(benchmarked_clauses) - favorable
        
        if unfavorable > favorable:
            insights.append(
                f"This agreement has more investor-friendly terms than typical {funding_stage} deals"
            )
        else:
            insights.append(
                f"This agreement has balanced or founder-friendly terms for {funding_stage}"
            )
        
        # Identify outliers
        outliers = [c for c in benchmarked_clauses if c.get("your_percentile", 50) > 75]
        if outliers:
            insights.append(
                f"{len(outliers)} clauses are significantly worse than market standard"
            )
        
        return {
            "insights": insights,
            "favorable_clause_count": favorable,
            "unfavorable_clause_count": unfavorable,
            "outlier_count": len(outliers)
        }
    
    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_overall_assessment(self, comparisons: List[Dict]) -> str:
        """Generate overall assessment"""
        good_count = sum(1 for c in comparisons if c.get("percentile", 50) <= 50)
        total = len(comparisons)
        
        if good_count / total > 0.7:
            return "Overall, this is a founder-friendly deal with competitive terms."
        elif good_count / total > 0.4:
            return "This deal has a mix of favorable and unfavorable terms."
        else:
            return "This deal is heavily investor-favorable. Strong negotiation recommended."
    
    def _get_trend_recommendation(self, clause_type: str, stage_data: Dict) -> str:
        """Get recommendation based on trends"""
        frequency = stage_data.get("frequency", 0)
        
        if frequency > 90:
            return f"Standard clause - appears in {frequency}% of deals"
        elif frequency > 70:
            return f"Common clause - appears in {frequency}% of deals"
        else:
            return f"Optional clause - only {frequency}% include this"
