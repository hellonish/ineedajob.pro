"""
Discrepancy Formatter - UI-friendly table formatting.

Transforms ProfileDiscrepancy results into table-ready formats.
"""

from typing import Dict, List, Union
from .models import ProfileDiscrepancy, ProfileItem


class TableFormatter:
    """
    Formats discrepancy results for UI display.
    
    Provides multiple table views:
    - Comparison table: All items with values from each source
    - Skill table: Skills matrix (backward compatible)
    - Discrepancy table: Detailed conflicts with severity
    
    Example:
        >>> formatter = TableFormatter()
        >>> tables = formatter.format_all(discrepancy_result)
        >>> print(tables['comparison_table'])
    """
    
    def format_comparison_table(self, result: Union[ProfileDiscrepancy, Dict]) -> Dict:
        """
        Format the complete comparison table showing all items.
        
        Args:
            result: ProfileDiscrepancy or dict with comparison data
            
        Returns:
            Dict with headers and rows ready for UI table rendering
        """
        items = self._get_comparison_items(result)
        
        return {
            "headers": ["Category", "Field", "Resume", "LinkedIn", "Portfolio", "Status"],
            "rows": [
                [
                    item.get("category", ""),
                    item.get("field", ""),
                    item.get("resume_value", "") or "-",
                    item.get("linkedin_value", "") or "-",
                    item.get("portfolio_value", "") or "-",
                    self._format_status(item.get("status", "match"))
                ]
                for item in items
            ]
        }
    
    def format_mismatches_table(self, result: Union[ProfileDiscrepancy, Dict]) -> Dict:
        """
        Format only mismatched items (different values across sources).
        
        Args:
            result: ProfileDiscrepancy or dict
            
        Returns:
            Dict with headers and rows for mismatches only
        """
        items = self._get_items(result, "mismatches")
        
        return {
            "headers": ["Category", "Field", "Resume", "LinkedIn", "Portfolio"],
            "rows": [
                [
                    item.get("category", ""),
                    item.get("field", ""),
                    item.get("resume_value", "") or "-",
                    item.get("linkedin_value", "") or "-",
                    item.get("portfolio_value", "") or "-"
                ]
                for item in items
            ]
        }
    
    def format_partial_table(self, result: Union[ProfileDiscrepancy, Dict]) -> Dict:
        """
        Format items missing from at least one source.
        
        Args:
            result: ProfileDiscrepancy or dict
            
        Returns:
            Dict with headers and rows for partial presence items
        """
        items = self._get_items(result, "partial_presence")
        
        return {
            "headers": ["Category", "Field", "Resume", "LinkedIn", "Portfolio"],
            "rows": [
                [
                    item.get("category", ""),
                    item.get("field", ""),
                    "✓" if item.get("resume_value") else "✗",
                    "✓" if item.get("linkedin_value") else "✗",
                    "✓" if item.get("portfolio_value") else "✗"
                ]
                for item in items
            ]
        }
    
    def format_skill_table(self, result: Union[ProfileDiscrepancy, Dict]) -> Dict:
        """
        Format skill comparison table (backward compatible).
        
        Args:
            result: ProfileDiscrepancy or dict
            
        Returns:
            Dict with skill comparison headers and rows
        """
        if isinstance(result, ProfileDiscrepancy):
            skills = [s.model_dump() for s in result.skill_comparison]
        else:
            skills = result.get("skill_comparison", [])
        
        return {
            "headers": ["Skill", "Resume", "LinkedIn", "Portfolio"],
            "rows": [
                [
                    skill.get("skill", ""),
                    "✓" if skill.get("in_resume") else "✗",
                    "✓" if skill.get("in_linkedin") else "✗",
                    "✓" if skill.get("in_portfolio") else "✗"
                ]
                for skill in skills
            ]
        }
    
    def format_discrepancy_table(self, result: Union[ProfileDiscrepancy, Dict]) -> Dict:
        """
        Format detailed discrepancy table with severity.
        
        Args:
            result: ProfileDiscrepancy or dict
            
        Returns:
            Dict with discrepancy details including issue and severity
        """
        if isinstance(result, ProfileDiscrepancy):
            discrepancies = [d.model_dump() for d in result.discrepancies]
        else:
            discrepancies = result.get("discrepancies", [])
        
        return {
            "headers": ["Field", "Resume", "LinkedIn", "Portfolio", "Issue", "Severity"],
            "rows": [
                [
                    d.get("field", ""),
                    d.get("resume", "") or "-",
                    d.get("linkedin", "") or "-",
                    d.get("portfolio", "") or "-",
                    d.get("issue", ""),
                    self._format_severity(d.get("severity", "low"))
                ]
                for d in discrepancies
            ]
        }
    
    def format_all(self, result: Union[ProfileDiscrepancy, Dict]) -> Dict:
        """
        Format complete result with all table views.
        
        Args:
            result: ProfileDiscrepancy or dict
            
        Returns:
            Dict with all formatted tables and summary data
        """
        if isinstance(result, ProfileDiscrepancy):
            result_dict = result.model_dump()
        else:
            result_dict = result
        
        return {
            # Main comparison table
            "comparison_table": self.format_comparison_table(result),
            
            # Filtered views
            "mismatches_table": self.format_mismatches_table(result),
            "partial_table": self.format_partial_table(result),
            
            # Legacy tables
            "skill_table": self.format_skill_table(result),
            "discrepancy_table": self.format_discrepancy_table(result),
            
            # Summary data
            "consistency_score": result_dict.get("consistency_score", 100),
            "recommendations": result_dict.get("recommendations", []),
            
            # Counts for UI badges
            "counts": {
                "total_items": len(result_dict.get("comparison_table", [])),
                "mismatches": len(result_dict.get("mismatches", [])),
                "partial": len(result_dict.get("partial_presence", [])),
                "consistent": len(result_dict.get("fully_consistent", []))
            }
        }
    
    # ========================================================================
    # PRIVATE HELPERS
    # ========================================================================
    
    def _get_comparison_items(self, result: Union[ProfileDiscrepancy, Dict]) -> List[Dict]:
        """Extract comparison table items from result."""
        if isinstance(result, ProfileDiscrepancy):
            return [item.model_dump() for item in result.comparison_table]
        return result.get("comparison_table", [])
    
    def _get_items(self, result: Union[ProfileDiscrepancy, Dict], key: str) -> List[Dict]:
        """Extract items by key from result."""
        if isinstance(result, ProfileDiscrepancy):
            items = getattr(result, key, [])
            return [item.model_dump() for item in items]
        return result.get(key, [])
    
    def _format_status(self, status: str) -> str:
        """Format status with emoji indicator."""
        status_map = {
            "match": "✅ Match",
            "mismatch": "⚠️ Mismatch",
            "partial": "📝 Partial"
        }
        return status_map.get(status, status)
    
    def _format_severity(self, severity: str) -> str:
        """Format severity with emoji indicator."""
        severity_map = {
            "high": "🔴 High",
            "medium": "🟡 Medium",
            "low": "🟢 Low"
        }
        return severity_map.get(severity, severity)


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def format_for_table(discrepancy_result: Union[ProfileDiscrepancy, Dict]) -> Dict:
    """
    Convenience function to format discrepancy results for UI.
    
    Args:
        discrepancy_result: ProfileDiscrepancy or dict result
        
    Returns:
        Dict with all formatted tables ready for rendering
    """
    formatter = TableFormatter()
    return formatter.format_all(discrepancy_result)
