"""
Multi-Jurisdiction Compliance Checker
Validates agreements against legal requirements in different jurisdictions
"""
from typing import Dict, Any, List
import re
from datetime import datetime


class ComplianceChecker:
    """Check agreement compliance across jurisdictions"""
    
    # Compliance rules database
    COMPLIANCE_RULES = {
        "US": {
            "framework": "US Securities Law",
            "rules": [
                {
                    "rule_id": "US-001",
                    "name": "Accredited Investor Verification",
                    "description": "Must verify investor accreditation status",
                    "severity": "critical",
                    "keywords": ["accredited investor", "verification", "net worth"],
                    "required": True
                },
                {
                    "rule_id": "US-002",
                    "name": "Blue Sky Laws Compliance",
                    "description": "State securities laws compliance",
                    "severity": "high",
                    "keywords": ["state securities", "registration", "exemption"],
                    "required": True
                },
                {
                    "rule_id": "US-003",
                    "name": "Right of First Refusal",
                    "description": "ROFR clauses must be clearly defined",
                    "severity": "medium",
                    "keywords": ["right of first refusal", "ROFR", "transfer restrictions"],
                    "required": False
                }
            ]
        },
        "EU": {
            "framework": "GDPR & EU Company Law",
            "rules": [
                {
                    "rule_id": "EU-001",
                    "name": "GDPR Data Protection",
                    "description": "Data processing and privacy requirements",
                    "severity": "critical",
                    "keywords": ["data protection", "privacy", "GDPR", "personal data"],
                    "required": True
                },
                {
                    "rule_id": "EU-002",
                    "name": "Shareholder Rights Directive",
                    "description": "Shareholder voting and information rights",
                    "severity": "high",
                    "keywords": ["shareholder rights", "voting", "information rights"],
                    "required": True
                },
                {
                    "rule_id": "EU-003",
                    "name": "Cross-Border Investment",
                    "description": "Cross-border investment regulations",
                    "severity": "medium",
                    "keywords": ["cross-border", "foreign investment", "regulatory"],
                    "required": False
                }
            ]
        },
        "UK": {
            "framework": "Companies Act 2006",
            "rules": [
                {
                    "rule_id": "UK-001",
                    "name": "Director Duties",
                    "description": "Director fiduciary duties and conflicts",
                    "severity": "high",
                    "keywords": ["director", "fiduciary", "duty", "conflict of interest"],
                    "required": True
                },
                {
                    "rule_id": "UK-002",
                    "name": "Financial Promotion Rules",
                    "description": "FCA financial promotion requirements",
                    "severity": "high",
                    "keywords": ["financial promotion", "FCA", "authorized person"],
                    "required": True
                },
                {
                    "rule_id": "UK-003",
                    "name": "Pre-emption Rights",
                    "description": "Statutory pre-emption rights on share issues",
                    "severity": "medium",
                    "keywords": ["pre-emption", "share issue", "existing shareholders"],
                    "required": True
                }
            ]
        },
        "India": {
            "framework": "Companies Act 2013",
            "rules": [
                {
                    "rule_id": "IN-001",
                    "name": "Foreign Investment Limits",
                    "description": "FDI sector limits and approval requirements",
                    "severity": "critical",
                    "keywords": ["foreign investment", "FDI", "FIPB", "RBI approval"],
                    "required": True
                },
                {
                    "rule_id": "IN-002",
                    "name": "Related Party Transactions",
                    "description": "RPT disclosure and approval requirements",
                    "severity": "high",
                    "keywords": ["related party", "RPT", "disclosure", "approval"],
                    "required": True
                },
                {
                    "rule_id": "IN-003",
                    "name": "FEMA Compliance",
                    "description": "Foreign Exchange Management Act compliance",
                    "severity": "high",
                    "keywords": ["FEMA", "foreign exchange", "pricing guidelines"],
                    "required": True
                }
            ]
        },
        "Singapore": {
            "framework": "Companies Act & Securities Act",
            "rules": [
                {
                    "rule_id": "SG-001",
                    "name": "Prospectus Requirements",
                    "description": "Exemptions from prospectus requirements",
                    "severity": "critical",
                    "keywords": ["prospectus", "exemption", "offer information"],
                    "required": True
                },
                {
                    "rule_id": "SG-002",
                    "name": "Director Obligations",
                    "description": "Director statutory duties and liabilities",
                    "severity": "high",
                    "keywords": ["director obligations", "statutory duties", "ACRA"],
                    "required": True
                },
                {
                    "rule_id": "SG-003",
                    "name": "Nominee Shareholders",
                    "description": "Nominee arrangements and beneficial ownership",
                    "severity": "medium",
                    "keywords": ["nominee", "beneficial owner", "transparency"],
                    "required": False
                }
            ]
        }
    }
    
    def __init__(self):
        """Initialize compliance checker"""
        print("✅ Compliance Checker initialized")
    
    def check_compliance(
        self,
        document_text: str,
        clauses: List[Dict[str, Any]],
        jurisdictions: List[str] = ["US"]
    ) -> Dict[str, Any]:
        """
        Check document compliance across jurisdictions
        
        Args:
            document_text: Full document text
            clauses: Extracted clauses
            jurisdictions: List of jurisdictions to check
            
        Returns:
            Compliance report with violations and recommendations
        """
        print(f"🔍 Checking compliance for: {', '.join(jurisdictions)}")
        
        results = {}
        for jurisdiction in jurisdictions:
            if jurisdiction not in self.COMPLIANCE_RULES:
                print(f"⚠️ No rules for {jurisdiction}, skipping")
                continue
            
            results[jurisdiction] = self._check_jurisdiction(
                document_text, clauses, jurisdiction
            )
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "jurisdictions_checked": jurisdictions,
            "results": results,
            "summary": summary
        }
    
    def _check_jurisdiction(
        self,
        doc_text: str,
        clauses: List[Dict],
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Check compliance for a specific jurisdiction"""
        rules = self.COMPLIANCE_RULES[jurisdiction]
        doc_lower = doc_text.lower()
        
        violations = []
        warnings = []
        compliant = []
        missing_clauses = []
        
        for rule in rules["rules"]:
            # Check if rule keywords appear in document
            found = any(
                keyword.lower() in doc_lower
                for keyword in rule["keywords"]
            )
            
            if rule["required"] and not found:
                violations.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "issue": "Required clause missing",
                    "fix": f"Add clause addressing: {rule['description']}"
                })
                missing_clauses.append(rule["name"])
            elif rule["required"] and found:
                compliant.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "status": "Found"
                })
            elif not rule["required"] and not found:
                warnings.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "description": rule["description"],
                    "recommendation": f"Consider adding: {rule['description']}"
                })
        
        # Calculate compliance score
        total_required = sum(1 for r in rules["rules"] if r["required"])
        compliant_count = len(compliant)
        compliance_score = (compliant_count / total_required * 100) if total_required > 0 else 100
        
        # Determine status
        if len(violations) == 0:
            status = "compliant"
        elif len(violations) > 0 and any(v["severity"] == "critical" for v in violations):
            status = "critical_violation"
        else:
            status = "needs_review"
        
        return {
            "framework": rules["framework"],
            "status": status,
            "compliance_score": round(compliance_score, 1),
            "violations": violations,
            "warnings": warnings,
            "compliant_rules": compliant,
            "missing_clauses": missing_clauses,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def _generate_summary(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate overall compliance summary"""
        total_violations = sum(
            len(r.get("violations", []))
            for r in results.values()
        )
        
        total_warnings = sum(
            len(r.get("warnings", []))
            for r in results.values()
        )
        
        critical_issues = []
        for jurisdiction, result in results.items():
            for violation in result.get("violations", []):
                if violation["severity"] == "critical":
                    critical_issues.append({
                        "jurisdiction": jurisdiction,
                        "issue": violation["rule_name"]
                    })
        
        # Overall status
        if total_violations == 0:
            overall_status = "compliant"
            risk_level = "low"
        elif len(critical_issues) > 0:
            overall_status = "critical_violations"
            risk_level = "critical"
        elif total_violations > 3:
            overall_status = "multiple_violations"
            risk_level = "high"
        else:
            overall_status = "minor_issues"
            risk_level = "medium"
        
        return {
            "overall_status": overall_status,
            "risk_level": risk_level,
            "total_violations": total_violations,
            "total_warnings": total_warnings,
            "critical_issues": critical_issues,
            "requires_action": total_violations > 0
        }
    
    def get_jurisdiction_requirements(self, jurisdiction: str) -> Dict[str, Any]:
        """Get all requirements for a jurisdiction"""
        if jurisdiction not in self.COMPLIANCE_RULES:
            return {"error": f"No rules available for {jurisdiction}"}
        
        rules_data = self.COMPLIANCE_RULES[jurisdiction]
        return {
            "jurisdiction": jurisdiction,
            "framework": rules_data["framework"],
            "total_rules": len(rules_data["rules"]),
            "required_clauses": [
                r["name"] for r in rules_data["rules"] if r["required"]
            ],
            "optional_clauses": [
                r["name"] for r in rules_data["rules"] if not r["required"]
            ],
            "all_rules": rules_data["rules"]
        }
    
    def suggest_fixes(
        self,
        compliance_result: Dict[str, Any],
        jurisdiction: str
    ) -> List[Dict[str, Any]]:
        """Suggest specific fixes for compliance violations"""
        fixes = []
        
        violations = compliance_result.get("violations", [])
        for violation in violations:
            fix = {
                "rule_id": violation["rule_id"],
                "rule_name": violation["rule_name"],
                "severity": violation["severity"],
                "suggested_clause": self._generate_template_clause(violation),
                "explanation": violation["description"],
                "priority": 1 if violation["severity"] == "critical" else 2
            }
            fixes.append(fix)
        
        # Sort by priority
        fixes.sort(key=lambda x: x["priority"])
        
        return fixes
    
    def _generate_template_clause(self, violation: Dict[str, Any]) -> str:
        """Generate template clause to fix violation"""
        templates = {
            "US-001": "The parties acknowledge that the investor is an 'accredited investor' as defined in Rule 501 of Regulation D under the Securities Act of 1933.",
            "US-002": "This offering is made in reliance on exemptions from registration under state securities laws.",
            "EU-001": "The parties agree to comply with GDPR requirements for data processing and protection of personal information.",
            "UK-001": "Directors shall act in accordance with their fiduciary duties as set forth in the Companies Act 2006.",
            "IN-001": "This investment complies with Foreign Direct Investment (FDI) regulations and sectoral caps as prescribed by DPIIT.",
            "SG-001": "This offering is made pursuant to an exemption from the prospectus requirements under the Securities and Futures Act."
        }
        
        return templates.get(
            violation["rule_id"],
            f"[Insert clause addressing: {violation['description']}]"
        )
