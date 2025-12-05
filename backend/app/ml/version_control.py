"""
Document Version Control System
Git-like tracking of agreement changes with diff visualization
"""
from typing import Dict, Any, List, Optional
import difflib
from datetime import datetime
import hashlib


class VersionControl:
    """Track document versions and changes"""
    
    def __init__(self):
        """Initialize version control system"""
        self.versions = {}  # In-memory storage (would use DB in production)
        print("✅ Version Control initialized")
    
    def create_version(
        self,
        document_id: str,
        content: str,
        clauses: List[Dict[str, Any]],
        created_by: str,
        change_summary: str = "",
        previous_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new document version
        
        Args:
            document_id: Document identifier
            content: Full document content
            clauses: Extracted clauses
            created_by: User who created this version
            change_summary: Summary of changes
            previous_version: Previous version number
            
        Returns:
            Version information
        """
        if document_id not in self.versions:
            self.versions[document_id] = []
        
        version_number = len(self.versions[document_id]) + 1
        
        # Calculate changes if there's a previous version
        changes = None
        risk_delta = 0
        if previous_version and len(self.versions[document_id]) > 0:
            prev = self.versions[document_id][previous_version - 1]
            changes = self._calculate_changes(prev, content, clauses)
            risk_delta = self._calculate_risk_delta(prev, clauses)
        
        # Create version record
        version = {
            "version_number": version_number,
            "document_id": document_id,
            "content": content,
            "content_hash": self._hash_content(content),
            "clauses": clauses,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": created_by,
            "change_summary": change_summary,
            "changes": changes,
            "risk_delta": risk_delta,
            "total_clauses": len(clauses)
        }
        
        self.versions[document_id].append(version)
        
        return {
            "version_number": version_number,
            "document_id": document_id,
            "created_at": version["created_at"],
            "changes_summary": changes,
            "risk_delta": risk_delta
        }
    
    def get_version_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a document"""
        if document_id not in self.versions:
            return []
        
        return [{
            "version_number": v["version_number"],
            "created_at": v["created_at"],
            "created_by": v["created_by"],
            "change_summary": v["change_summary"],
            "total_clauses": v["total_clauses"],
            "risk_delta": v.get("risk_delta", 0)
        } for v in self.versions[document_id]]
    
    def compare_versions(
        self,
        document_id: str,
        version_a: int,
        version_b: int
    ) -> Dict[str, Any]:
        """
        Compare two versions and show differences
        
        Args:
            document_id: Document identifier
            version_a: First version number
            version_b: Second version number
            
        Returns:
            Detailed diff information
        """
        if document_id not in self.versions:
            raise ValueError(f"Document {document_id} not found")
        
        versions = self.versions[document_id]
        
        if version_a < 1 or version_a > len(versions):
            raise ValueError(f"Invalid version A: {version_a}")
        if version_b < 1 or version_b > len(versions):
            raise ValueError(f"Invalid version B: {version_b}")
        
        v_a = versions[version_a - 1]
        v_b = versions[version_b - 1]
        
        # Text diff
        text_diff = self._generate_text_diff(
            v_a["content"],
            v_b["content"]
        )
        
        # Clause-level changes
        clause_changes = self._compare_clauses(
            v_a["clauses"],
            v_b["clauses"]
        )
        
        # Risk comparison
        risk_comparison = self._compare_risks(
            v_a["clauses"],
            v_b["clauses"]
        )
        
        return {
            "document_id": document_id,
            "version_a": version_a,
            "version_b": version_b,
            "text_diff": text_diff,
            "clause_changes": clause_changes,
            "risk_comparison": risk_comparison,
            "recommendation": self._recommend_version(v_a, v_b)
        }
    
    def _calculate_changes(
        self,
        previous_version: Dict,
        new_content: str,
        new_clauses: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate what changed between versions"""
        # Compare clause counts
        prev_clause_count = len(previous_version["clauses"])
        new_clause_count = len(new_clauses)
        
        clauses_added = max(0, new_clause_count - prev_clause_count)
        clauses_removed = max(0, prev_clause_count - new_clause_count)
        
        # Find modified clauses
        prev_clause_types = {c["clause_type"]: c for c in previous_version["clauses"]}
        new_clause_types = {c["clause_type"]: c for c in new_clauses}
        
        clauses_modified = 0
        for clause_type, new_clause in new_clause_types.items():
            if clause_type in prev_clause_types:
                prev_clause = prev_clause_types[clause_type]
                if prev_clause["clause_text"] != new_clause["clause_text"]:
                    clauses_modified += 1
        
        return {
            "clauses_added": clauses_added,
            "clauses_removed": clauses_removed,
            "clauses_modified": clauses_modified,
            "total_changes": clauses_added + clauses_removed + clauses_modified
        }
    
    def _calculate_risk_delta(
        self,
        previous_version: Dict,
        new_clauses: List[Dict]
    ) -> float:
        """Calculate change in risk score"""
        # Calculate average risk for previous version
        prev_risks = [c.get("risk_score", 0) for c in previous_version["clauses"]]
        prev_avg = sum(prev_risks) / len(prev_risks) if prev_risks else 0
        
        # Calculate average risk for new version
        new_risks = [c.get("risk_score", 0) for c in new_clauses]
        new_avg = sum(new_risks) / len(new_risks) if new_risks else 0
        
        # Positive delta means risk increased
        return round(new_avg - prev_avg, 2)
    
    def _generate_text_diff(self, text_a: str, text_b: str) -> List[Dict[str, Any]]:
        """Generate line-by-line diff"""
        lines_a = text_a.split('\n')
        lines_b = text_b.split('\n')
        
        diff = list(difflib.unified_diff(
            lines_a,
            lines_b,
            lineterm='',
            n=3  # Context lines
        ))
        
        # Parse diff into structured format
        changes = []
        for line in diff[2:]:  # Skip header lines
            if line.startswith('+'):
                changes.append({
                    "type": "addition",
                    "content": line[1:].strip()
                })
            elif line.startswith('-'):
                changes.append({
                    "type": "deletion",
                    "content": line[1:].strip()
                })
            elif line.startswith(' '):
                changes.append({
                    "type": "context",
                    "content": line[1:].strip()
                })
        
        return changes[:50]  # Limit to first 50 changes
    
    def _compare_clauses(
        self,
        clauses_a: List[Dict],
        clauses_b: List[Dict]
    ) -> Dict[str, Any]:
        """Compare clauses between versions"""
        types_a = {c["clause_type"] for c in clauses_a}
        types_b = {c["clause_type"] for c in clauses_b}
        
        added = types_b - types_a
        removed = types_a - types_b
        common = types_a & types_b
        
        modified = []
        for clause_type in common:
            clause_a = next(c for c in clauses_a if c["clause_type"] == clause_type)
            clause_b = next(c for c in clauses_b if c["clause_type"] == clause_type)
            
            if clause_a["clause_text"] != clause_b["clause_text"]:
                modified.append({
                    "clause_type": clause_type,
                    "risk_before": clause_a.get("risk_level", "unknown"),
                    "risk_after": clause_b.get("risk_level", "unknown"),
                    "risk_score_delta": clause_b.get("risk_score", 0) - clause_a.get("risk_score", 0)
                })
        
        return {
            "added_clauses": list(added),
            "removed_clauses": list(removed),
            "modified_clauses": modified,
            "unchanged_clauses": len(common) - len(modified)
        }
    
    def _compare_risks(
        self,
        clauses_a: List[Dict],
        clauses_b: List[Dict]
    ) -> Dict[str, Any]:
        """Compare risk profiles"""
        def count_by_risk(clauses):
            counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            for c in clauses:
                risk = c.get("risk_level", "medium")
                if risk in counts:
                    counts[risk] += 1
            return counts
        
        risk_a = count_by_risk(clauses_a)
        risk_b = count_by_risk(clauses_b)
        
        return {
            "version_a_risks": risk_a,
            "version_b_risks": risk_b,
            "risk_delta": {
                level: risk_b[level] - risk_a[level]
                for level in risk_a.keys()
            }
        }
    
    def _recommend_version(self, version_a: Dict, version_b: Dict) -> str:
        """Recommend which version is better"""
        # Calculate risk scores
        risk_a = sum(c.get("risk_score", 0) for c in version_a["clauses"])
        risk_b = sum(c.get("risk_score", 0) for c in version_b["clauses"])
        
        if risk_b < risk_a:
            return f"Version {version_b['version_number']} is better (lower risk score)"
        elif risk_a < risk_b:
            return f"Version {version_a['version_number']} is better (lower risk score)"
        else:
            return "Both versions have similar risk profiles"
    
    def _hash_content(self, content: str) -> str:
        """Generate hash of content for tracking"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def rollback_to_version(
        self,
        document_id: str,
        version_number: int
    ) -> Dict[str, Any]:
        """Rollback to a previous version"""
        if document_id not in self.versions:
            raise ValueError(f"Document {document_id} not found")
        
        versions = self.versions[document_id]
        if version_number < 1 or version_number > len(versions):
            raise ValueError(f"Invalid version: {version_number}")
        
        target_version = versions[version_number - 1]
        
        return {
            "success": True,
            "rolled_back_to": version_number,
            "content": target_version["content"],
            "clauses": target_version["clauses"],
            "message": f"Rolled back to version {version_number}"
        }
