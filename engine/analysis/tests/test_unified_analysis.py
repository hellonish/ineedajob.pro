"""Test Unified Analysis - Single entry point for all 3 analyses."""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.analysis import UnifiedAnalyzer, analyze_resume


def test_unified_analysis():
    print(f"\n{'='*70}")
    print("Testing Unified Analysis")
    print(f"{'='*70}\n")
    
    # Load test data
    test_dir = os.path.dirname(__file__)
    
    with open(os.path.join(test_dir, 'job_result.json'), 'r') as f:
        job_posting = json.load(f)
    
    with open(os.path.join(test_dir, 'profile.json'), 'r') as f:
        profile_data = json.load(f)
    
    resume = profile_data.get('sources', {}).get('resume', profile_data.get('unified_profile', {}))
    unified_profile = profile_data.get('unified_profile', {})
    
    print("✓ Loaded job posting and profile data")
    
    # Run unified analysis
    today_date = "2026-01-15"
    result = analyze_resume(
        job_posting=job_posting,
        resume=resume,
        unified_profile=unified_profile,
        today_date=today_date
    )
    
    # Display results
    print(f"\n{'='*70}")
    print("UNIFIED ANALYSIS RESULTS")
    print(f"{'='*70}\n")
    
    # Scores summary
    print("📊 SCORES:")
    print(f"  • Qualification Match: {result.qualification_match_score:.1f}%")
    print(f"  • Skill Match: {result.skill_match_score:.1f}%")
    print(f"  • Formatting Score: {result.resume_formatting_score}/100")
    print(f"  • Keyword Match: {result.keyword_match_score:.1f}%")
    print(f"  ─────────────────────────")
    print(f"  📈 FINAL SCORE: {result.final_score:.1f}%")
    
    # Qualifications
    print(f"\n📌 Required Qualifications ({result.required_matched}/{result.required_total}):")
    for q in result.required_qualifications:
        status = "✓" if q.matched else "✗"
        print(f"  {status} {q.name[:60]}...")
    
    print(f"\n💻 Technical Skills ({result.technical_matched}/{result.technical_total}):")
    for q in result.technical_skills:
        status = "✓" if q.matched else "✗"
        print(f"  {status} {q.name}")
    
    print(f"\n🤝 Soft Skills ({result.soft_matched}/{result.soft_total}):")
    for q in result.soft_skills:
        status = "✓" if q.matched else "✗"
        print(f"  {status} {q.name}")
    
    # Chronological issues
    print(f"\n📅 Chronological Issues ({len(result.chronological_issues)}):")
    for issue in result.chronological_issues:
        print(f"  ⚠ [{issue['section']}] {issue['description'][:50]}...")
    if not result.chronological_issues:
        print("  ✓ No chronological issues found")
    
    # Suggestions
    print(f"\n💡 Resume Suggestions ({len(result.resume_suggestions)}):")
    for sug in result.resume_suggestions[:5]:
        icon = "➕" if sug['action'] == "ADD" else "✏️" if sug['action'] == "UPDATE" else "🗑️"
        print(f"  {icon} [{sug['action']}] {sug['section']}")
        print(f"      {sug['suggestion'][:60]}...")
    
    # Compensation
    print(f"\n💰 Compensation & Benefits:")
    print(f"  Salary: {result.salary_range}")
    print(f"  Benefits: {', '.join(result.compensation_and_benefits[:5])}")
    
    # Save output
    output_path = os.path.join(test_dir, 'unified_analysis_result.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    print(f"\n💾 Saved to: unified_analysis_result.json")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_unified_analysis()
