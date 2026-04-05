"""
Discrepancy Detection Module.

Compares Resume, LinkedIn, and Portfolio profiles to find inconsistencies.
"""

from .checker import compare_profile_sources, format_for_table
from .models import (
    ProfileDiscrepancy,
    ProfileItem,
    DiscrepancyItem,
    SkillComparison
)
from .analyzer import DiscrepancyAnalyzer
from .formatter import TableFormatter

__all__ = [
    # Main functions (backward compatible)
    'compare_profile_sources',
    'format_for_table',
    
    # OOP classes
    'DiscrepancyAnalyzer',
    'TableFormatter',
    
    # Models
    'ProfileDiscrepancy',
    'ProfileItem',
    'DiscrepancyItem',
    'SkillComparison'
]
