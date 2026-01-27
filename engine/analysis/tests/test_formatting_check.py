"""Test Formatting Check"""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.analysis.formatting_check import FormattingChecker


def test_formatting_check():
    print(f"\n{'='*70}")
    print("Testing Formatting Check")
    print(f"{'='*70}\n")
    
    # Load test data
    test_dir = os.path.dirname(__file__)
    
    with open(os.path.join(test_dir, 'profile.json'), 'r') as f:
        profile_data = json.load(f)
    
    resume = profile_data.get('sources', {}).get('resume', profile_data.get('unified_profile', {}))
    
    print("✓ Loaded resume")
    
    # Get today's date
    today_date = "2026-01-15"  # Current date
    print(f"✓ Using date: {today_date}")
    
    # Run check
    checker = FormattingChecker()
    result = checker.check(resume, today_date=today_date)
    
    # Display results
    print(f"\n{'='*70}")
    print("FORMATTING CHECK RESULTS")
    print(f"{'='*70}\n")
    
    print(f"📊 Overall Quality Score: {result.overall_quality_score}/100")
    
    print(f"\n📝 Formatting Issues ({result.total_formatting_issues}):")
    for issue in result.formatting_issues:
        severity_icon = "🔴" if issue.severity == "high" else "🟡" if issue.severity == "medium" else "🟢"
        print(f"  {severity_icon} [{issue.section}] {issue.description[:60]}...")
        if issue.suggestion:
            print(f"      Suggestion: {issue.suggestion[:50]}...")
    
    print(f"\n📅 Chronological Issues ({result.total_chronological_issues}):")
    for issue in result.chronological_issues:
        print(f"  ⚠ [{issue.issue_type}] {issue.description[:60]}...")
        if issue.affected_items:
            print(f"      Affected: {', '.join(issue.affected_items[:3])}")
    
    # Save output
    output_path = os.path.join(test_dir, 'formatting_check_result.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    print(f"\n💾 Saved to: formatting_check_result.json")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_formatting_check()
