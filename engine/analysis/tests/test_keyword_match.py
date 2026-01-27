"""Test Keyword Match"""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.analysis.keyword_match import KeywordMatcher


def test_keyword_match():
    print(f"\n{'='*70}")
    print("Testing Keyword Match")
    print(f"{'='*70}\n")
    
    # Load test data
    test_dir = os.path.dirname(__file__)
    
    with open(os.path.join(test_dir, 'job_result.json'), 'r') as f:
        job_posting = json.load(f)
    
    with open(os.path.join(test_dir, 'profile.json'), 'r') as f:
        profile_data = json.load(f)
    
    resume = profile_data.get('sources', {}).get('resume', profile_data.get('unified_profile', {}))
    unified_profile = profile_data.get('unified_profile', {})
    
    print("✓ Loaded job posting and resume")
    
    # Run match
    matcher = KeywordMatcher()
    result = matcher.match(job_posting, resume, unified_profile)
    
    # Display results
    print(f"\n{'='*70}")
    print("KEYWORD MATCH RESULTS")
    print(f"{'='*70}\n")
    
    print(f"📊 Keyword Match Score: {result.keyword_match_score}%")
    print(f"   ({result.matched_count}/{result.total_keywords} keywords found)")
    
    print(f"\n✓ Keywords Found ({len(result.keywords_found)}):")
    for kw in result.keywords_found[:10]:
        print(f"  • {kw}")
    if len(result.keywords_found) > 10:
        print(f"  ... and {len(result.keywords_found) - 10} more")
    
    print(f"\n✗ Keywords Missing ({len(result.keywords_missing)}):")
    for kw in result.keywords_missing:
        print(f"  • {kw}")
    
    print(f"\n💡 Suggestions ({len(result.suggestions)}):")
    for sug in result.suggestions[:5]:
        action_icon = "➕" if sug.action == "ADD" else "✏️" if sug.action == "UPDATE" else "🗑️"
        print(f"  {action_icon} [{sug.action}] {sug.section}")
        print(f"      {sug.suggestion[:70]}...")
        print(f"      Keyword: {sug.keyword_addressed}")
    
    # Save output
    output_path = os.path.join(test_dir, 'keyword_match_result.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    print(f"\n💾 Saved to: keyword_match_result.json")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_keyword_match()
