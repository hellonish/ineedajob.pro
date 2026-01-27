"""
Unified Analysis - Single entry point for all resume analysis.

Combines:
- Qualification Check
- Formatting Check  
- Keyword Match
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .qualification_check import QualificationChecker, QualificationMatch
from .formatting_check import FormattingChecker, ChronologicalIssue
from .keyword_match import KeywordMatcher, ResumeSuggestion


class QualificationItem(BaseModel):
    """Single qualification with match status."""
    name: str
    matched: bool
    evidence: str = ""


class AnalysisResult(BaseModel):
    """Combined analysis result from all 3 modules."""
    
    # Qualification matches (✓ or ✗)
    required_qualifications: List[QualificationItem] = Field(default_factory=list)
    preferred_qualifications: List[QualificationItem] = Field(default_factory=list)
    technical_skills: List[QualificationItem] = Field(default_factory=list)
    soft_skills: List[QualificationItem] = Field(default_factory=list)
    
    # Chronological issues from formatting check
    chronological_issues: List[Dict] = Field(default_factory=list)
    
    # Scores
    resume_formatting_score: int = Field(default=100)
    keyword_match_score: float = Field(default=0.0)
    qualification_match_score: float = Field(default=0.0)
    skill_match_score: float = Field(default=0.0)
    
    # Resume suggestions from keyword match
    resume_suggestions: List[Dict] = Field(default_factory=list)
    
    # Job info
    compensation_and_benefits: List[str] = Field(default_factory=list)
    salary_range: str = ""
    
    # Final weighted score
    final_score: float = Field(default=0.0)
    
    # Match counts for display
    required_matched: int = 0
    required_total: int = 0
    preferred_matched: int = 0
    preferred_total: int = 0
    technical_matched: int = 0
    technical_total: int = 0
    soft_matched: int = 0
    soft_total: int = 0


class UnifiedAnalyzer:
    """
    Single entry point for all resume analysis.
    
    Runs:
    1. Qualification Check
    2. Formatting Check
    3. Keyword Match
    
    Returns combined AnalysisResult with weighted final score.
    """
    
    # Weights for final score calculation
    WEIGHTS = {
        'qualification': 0.30,  # 30%
        'skill': 0.25,          # 25%
        'formatting': 0.20,     # 20%
        'keyword': 0.25         # 25%
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self.qualification_checker = QualificationChecker(api_key)
        self.formatting_checker = FormattingChecker(api_key)
        self.keyword_matcher = KeywordMatcher(api_key)
    
    def analyze(
        self,
        job_posting: Dict,
        resume: Dict,
        unified_profile: Optional[Dict] = None,
        today_date: Optional[str] = None
    ) -> AnalysisResult:
        """
        Run all 3 analyses and return combined result.
        
        Args:
            job_posting: Parsed job posting JSON
            resume: Resume data
            unified_profile: Full profile for context (optional)
            today_date: Today's date for chronological validation
            
        Returns:
            AnalysisResult with all data and weighted final score
        """
        print("="*60)
        print("🔍 UNIFIED ANALYSIS")
        print("="*60)
        
        if today_date is None:
            from datetime import date
            today_date = date.today().isoformat()
        
        # 1. Qualification Check
        print("\n📋 Step 1/3: Qualification Check")
        qual_result = self.qualification_checker.check(job_posting, resume)
        
        # 2. Formatting Check
        print("\n📝 Step 2/3: Formatting Check")
        format_result = self.formatting_checker.check(resume, today_date)
        
        # 3. Keyword Match
        print("\n🔑 Step 3/3: Keyword Match")
        keyword_result = self.keyword_matcher.match(job_posting, resume, unified_profile)
        
        # Build combined result
        result = self._build_result(job_posting, qual_result, format_result, keyword_result)
        
        print("\n" + "="*60)
        print(f"✅ ANALYSIS COMPLETE - Final Score: {result.final_score:.1f}%")
        print("="*60)
        
        return result
    
    def _build_result(self, job_posting, qual_result, format_result, keyword_result) -> AnalysisResult:
        """Combine all results into single AnalysisResult."""
        
        # Convert qualifications
        required = [
            QualificationItem(name=q.qualification, matched=q.matched, evidence=q.evidence)
            for q in qual_result.required_qualifications
        ]
        preferred = [
            QualificationItem(name=q.qualification, matched=q.matched, evidence=q.evidence)
            for q in qual_result.preferred_qualifications
        ]
        technical = [
            QualificationItem(name=q.qualification, matched=q.matched, evidence=q.evidence)
            for q in qual_result.technical_skills
        ]
        soft = [
            QualificationItem(name=q.qualification, matched=q.matched, evidence=q.evidence)
            for q in qual_result.soft_skills
        ]
        
        # Calculate match scores
        req_matched = sum(1 for q in required if q.matched)
        pref_matched = sum(1 for q in preferred if q.matched)
        tech_matched = sum(1 for q in technical if q.matched)
        soft_matched = sum(1 for q in soft if q.matched)
        
        qual_score = (req_matched / len(required) * 100) if required else 100
        skill_score = (tech_matched / len(technical) * 100) if technical else 100
        
        # Chronological issues
        chrono_issues = [
            {
                "section": issue.affected_items[0] if issue.affected_items else "",
                "issue_type": issue.issue_type,
                "description": issue.description
            }
            for issue in format_result.chronological_issues
        ]
        
        # Resume suggestions
        suggestions = [
            {
                "action": s.action,
                "section": s.section,
                "target": s.target,
                "suggestion": s.suggestion,
                "keyword": s.keyword_addressed
            }
            for s in keyword_result.suggestions
        ]
        
        # Calculate final weighted score
        final_score = (
            qual_score * self.WEIGHTS['qualification'] +
            skill_score * self.WEIGHTS['skill'] +
            format_result.overall_quality_score * self.WEIGHTS['formatting'] +
            keyword_result.keyword_match_score * self.WEIGHTS['keyword']
        )
        
        return AnalysisResult(
            required_qualifications=required,
            preferred_qualifications=preferred,
            technical_skills=technical,
            soft_skills=soft,
            chronological_issues=chrono_issues,
            resume_formatting_score=format_result.overall_quality_score,
            keyword_match_score=keyword_result.keyword_match_score,
            qualification_match_score=qual_score,
            skill_match_score=skill_score,
            resume_suggestions=suggestions,
            compensation_and_benefits=job_posting.get('compensation_and_benefits', []),
            salary_range=job_posting.get('salary_range', ''),
            final_score=round(final_score, 1),
            required_matched=req_matched,
            required_total=len(required),
            preferred_matched=pref_matched,
            preferred_total=len(preferred),
            technical_matched=tech_matched,
            technical_total=len(technical),
            soft_matched=soft_matched,
            soft_total=len(soft)
        )


# Convenience function
def analyze_resume(
    job_posting: Dict,
    resume: Dict,
    unified_profile: Optional[Dict] = None,
    today_date: Optional[str] = None,
    api_key: Optional[str] = None
) -> AnalysisResult:
    """
    Convenience function for unified analysis.
    """
    analyzer = UnifiedAnalyzer(api_key)
    return analyzer.analyze(job_posting, resume, unified_profile, today_date)
