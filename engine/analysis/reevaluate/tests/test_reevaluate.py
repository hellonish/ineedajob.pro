"""Test Re-evaluation - Scoring only, no suggestions."""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)

from engine.analysis.reevaluate import reevaluate_resume


def test_reevaluate():
    print(f"\n{'='*70}")
    print("Testing Re-evaluation (Scores Only)")
    print(f"{'='*70}\n")
    
    # Load test data
    test_dir = os.path.dirname(__file__)
    analysis_test_dir = os.path.join(os.path.dirname(os.path.dirname(test_dir)), 'tests')
    
    with open(os.path.join(analysis_test_dir, 'job_result.json'), 'r') as f:
        job_posting = json.load(f)
    
    with open(os.path.join(analysis_test_dir, 'profile.json'), 'r') as f:
        profile_data = json.load(f)
    
    # Use resume as "modified" resume (in real usage, user would have edited it)
    modified_resume = profile_data.get('sources', {}).get('resume', profile_data.get('unified_profile', {}))
    
    print("✓ Loaded job posting and modified resume")
    
    # Simulate previous score (from initial analysis)
    previous_score = 65.2
    print(f"✓ Previous score: {previous_score}%")
    
    # Run re-evaluation
    result = reevaluate_resume(
        job_posting=job_posting,
        modified_resume=modified_resume,
        today_date="2026-01-15",
        previous_score=previous_score
    )
    
    # Display results
    print(f"\n{'='*70}")
    print("RE-EVALUATION RESULTS (Scores Only)")
    print(f"{'='*70}\n")
    
    print("📊 SCORES:")
    print(f"  • Qualification: {result.qualification_match_score}% ({result.required_qualifications_matched}/{result.required_qualifications_total})")
    print(f"  • Technical Skills: {result.skill_match_score}% ({result.technical_skills_matched}/{result.technical_skills_total})")
    print(f"  • Formatting: {result.formatting_score}/100 ({result.formatting_issues_count} issues)")
    print(f"  • Keywords: {result.keyword_match_score}% ({result.keywords_found}/{result.keywords_total})")
    print(f"  ─────────────────────────")
    print(f"  📈 FINAL SCORE: {result.final_score}%")
    
    if result.score_change != 0:
        indicator = "📈" if result.improved else "📉"
        print(f"  {indicator} Change: {result.score_change:+.1f}%")
    
    # Save output
    output_path = os.path.join(test_dir, 'reevaluation_result.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    print(f"\n💾 Saved to: reevaluation_result.json")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_reevaluate()
