"""
Re-evaluator - Scoring-only analysis for modified resumes.

Runs the same analysis as UnifiedAnalyzer but returns only scores,
no suggestions. Used when user modifies their resume and wants to
see updated scores.
"""

from typing import Dict, Optional
from .models import ReEvaluationResult
from ..qualification_check import QualificationChecker
from ..formatting_check import FormattingChecker
from ..keyword_match import KeywordMatcher


class ReEvaluator:
    """
    Re-evaluates a modified resume and returns updated scores.
    
    Only returns scores - no suggestions. Designed for the 
    "Re-evaluate" button after user makes resume changes.
    """
    
    # Same weights as UnifiedAnalyzer
    WEIGHTS = {
        'qualification': 0.30,
        'skill': 0.25,
        'formatting': 0.20,
        'keyword': 0.25
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self.qualification_checker = QualificationChecker(api_key)
        self.formatting_checker = FormattingChecker(api_key)
        self.keyword_matcher = KeywordMatcher(api_key)
    
    def evaluate(
        self,
        job_posting: Dict,
        modified_resume: Dict,
        today_date: Optional[str] = None,
        previous_score: Optional[float] = None
    ) -> ReEvaluationResult:
        """
        Re-evaluate a modified resume and return scores only.
        
        Args:
            job_posting: Parsed job posting JSON
            modified_resume: The modified resume data
            today_date: Today's date for chronological checks
            previous_score: Previous final score (to calculate improvement)
            
        Returns:
            ReEvaluationResult with all scores
        """
        print("="*60)
        print("🔄 RE-EVALUATING RESUME")
        print("="*60)
        
        if today_date is None:
            from datetime import date
            today_date = date.today().isoformat()
        
        # 1. Qualification Check
        print("\n📋 Step 1/3: Qualification Check")
        qual_result = self.qualification_checker.check(job_posting, modified_resume)
        
        # 2. Formatting Check
        print("\n📝 Step 2/3: Formatting Check")
        format_result = self.formatting_checker.check(modified_resume, today_date)
        
        # 3. Keyword Match (skip suggestions in output)
        print("\n🔑 Step 3/3: Keyword Match")
        keyword_result = self.keyword_matcher.match(job_posting, modified_resume)
        
        # Calculate scores
        req_matched = sum(1 for q in qual_result.required_qualifications if q.matched)
        req_total = len(qual_result.required_qualifications)
        tech_matched = sum(1 for q in qual_result.technical_skills if q.matched)
        tech_total = len(qual_result.technical_skills)
        soft_matched = sum(1 for q in qual_result.soft_skills if q.matched)
        soft_total = len(qual_result.soft_skills)
        
        qual_score = (req_matched / req_total * 100) if req_total else 100
        skill_score = (tech_matched / tech_total * 100) if tech_total else 100
        
        # Final weighted score
        final_score = (
            qual_score * self.WEIGHTS['qualification'] +
            skill_score * self.WEIGHTS['skill'] +
            format_result.overall_quality_score * self.WEIGHTS['formatting'] +
            keyword_result.keyword_match_score * self.WEIGHTS['keyword']
        )
        
        # Calculate improvement
        score_change = 0.0
        improved = False
        if previous_score is not None:
            score_change = final_score - previous_score
            improved = score_change > 0
        
        result = ReEvaluationResult(
            required_qualifications_matched=req_matched,
            required_qualifications_total=req_total,
            qualification_match_score=round(qual_score, 1),
            technical_skills_matched=tech_matched,
            technical_skills_total=tech_total,
            soft_skills_matched=soft_matched,
            soft_skills_total=soft_total,
            skill_match_score=round(skill_score, 1),
            formatting_score=format_result.overall_quality_score,
            formatting_issues_count=format_result.total_formatting_issues,
            keyword_match_score=keyword_result.keyword_match_score,
            keywords_found=keyword_result.matched_count,
            keywords_total=keyword_result.total_keywords,
            final_score=round(final_score, 1),
            score_change=round(score_change, 1),
            improved=improved
        )
        
        print("\n" + "="*60)
        if previous_score is not None:
            change_indicator = "📈" if improved else "📉" if score_change < 0 else "➡️"
            print(f"{change_indicator} SCORE: {result.final_score}% (change: {score_change:+.1f}%)")
        else:
            print(f"✅ SCORE: {result.final_score}%")
        print("="*60)
        
        return result


# Convenience function
def reevaluate_resume(
    job_posting: Dict,
    modified_resume: Dict,
    today_date: Optional[str] = None,
    previous_score: Optional[float] = None,
    api_key: Optional[str] = None
) -> ReEvaluationResult:
    """
    Convenience function to re-evaluate a modified resume.
    
    Returns only scores, no suggestions.
    """
    evaluator = ReEvaluator(api_key)
    return evaluator.evaluate(job_posting, modified_resume, today_date, previous_score)
