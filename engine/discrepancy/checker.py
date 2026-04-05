"""
Profile Discrepancy Checker - Backward Compatible Wrapper.

This module provides backward-compatible functions that wrap the new OOP classes.
For new code, prefer using DiscrepancyAnalyzer and TableFormatter directly.
"""

from typing import Dict, Optional
from .analyzer import DiscrepancyAnalyzer
from .formatter import TableFormatter, format_for_table
from .models import (
    ProfileDiscrepancy,
    ProfileItem,
    DiscrepancyItem,
    SkillComparison
)


def compare_profile_sources(
    resume: Optional[Dict] = None,
    linkedin: Optional[Dict] = None,
    portfolio: Optional[Dict] = None,
    api_key: Optional[str] = None
) -> Dict:
    """
    Compare 3 profile sources to find discrepancies.
    
    Returns JSON formatted for UI table display.
    Uses 1 AI call.
    
    Args:
        resume: Parsed resume data
        linkedin: Parsed LinkedIn profile data
        portfolio: Parsed portfolio data
        api_key: DeepSeek API key (optional)
        
    Returns:
        Dict with:
        - comparison_table: All items with values from each source
        - mismatches: Items with different values
        - partial_presence: Items missing from some sources
        - fully_consistent: Items that match everywhere
        - discrepancies: Detailed conflict explanations
        - skill_comparison: Skills matrix (backward compat)
        - consistency_score: 0-100 percentage
        - recommendations: Specific fixes
        
    Example:
        >>> from profile import parse_profile
        >>> from discrepancy import compare_profile_sources
        >>> 
        >>> resume = json.loads(parse_profile("resume.pdf", "pdf"))
        >>> linkedin = json.loads(parse_profile("linkedin.pdf", "pdf"))
        >>> portfolio = json.loads(parse_profile("index.html", "html"))
        >>> 
        >>> result = compare_profile_sources(resume, linkedin, portfolio)
        >>> # result['comparison_table'] shows all items with values per source
    """
    try:
        analyzer = DiscrepancyAnalyzer(api_key)
        result = analyzer.analyze(resume, linkedin, portfolio)
        return result.model_dump()
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        print(f"  ⚠ Discrepancy analysis failed: {e}")
        return {"error": str(e)}


# Re-export format_for_table for backward compatibility
__all__ = [
    'compare_profile_sources',
    'format_for_table',
    'DiscrepancyAnalyzer',
    'TableFormatter',
    'ProfileDiscrepancy',
    'ProfileItem',
    'DiscrepancyItem',
    'SkillComparison'
]
