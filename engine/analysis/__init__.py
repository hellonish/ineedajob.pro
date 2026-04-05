"""
Analysis Module - Resume and Job Analysis Tools.

Sub-modules:
- qualification_check: Compare resume against job qualifications
- formatting_check: Analyze resume for formatting/chronological issues  
- keyword_match: Match job keywords and suggest improvements

Main Entry Point:
- UnifiedAnalyzer: Runs all 3 analyses and returns combined result
- analyze_resume: Convenience function
"""

from .qualification_check import QualificationChecker, QualificationCheckResult
from .formatting_check import FormattingChecker, FormattingCheckResult
from .keyword_match import KeywordMatcher, KeywordMatchResult
from .analyzer import UnifiedAnalyzer, AnalysisResult, analyze_resume

__all__ = [
    # Main entry point
    'UnifiedAnalyzer', 'AnalysisResult', 'analyze_resume',
    # Individual modules
    'QualificationChecker', 'QualificationCheckResult',
    'FormattingChecker', 'FormattingCheckResult',
    'KeywordMatcher', 'KeywordMatchResult',
]
