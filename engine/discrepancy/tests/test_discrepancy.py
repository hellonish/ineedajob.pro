"""
Test Profile Discrepancy Detector
Uses profile_data.json containing resume, linkedin, and portfolio data.
"""

import json
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Import directly from discrepancy submodule to avoid engine/__init__.py issues
from engine.discrepancy.checker import compare_profile_sources
from engine.discrepancy.formatter import TableFormatter, format_for_table


def load_test_profiles():
    """Load profiles from profile_data.json."""
    test_dir = os.path.dirname(__file__)
    profile_path = os.path.join(test_dir, 'profile_data.json')
    
    if not os.path.exists(profile_path):
        print(f"⚠ Profile data not found at {profile_path}")
        return {}
    
    with open(profile_path, 'r') as f:
        data = json.load(f)
    
    # The JSON has 'sources' key containing resume, linkedin, portfolio
    profiles = data.get('sources', {})
    
    loaded = []
    if profiles.get('resume'):
        loaded.append('resume')
    if profiles.get('linkedin'):
        loaded.append('linkedin')
    if profiles.get('portfolio'):
        loaded.append('portfolio')
    
    print(f"✓ Loaded profiles: {', '.join(loaded)}")
    return profiles


def test_discrepancy():
    """Test discrepancy detection with profile_data.json."""
    print(f"\n{'='*70}")
    print("Testing Profile Discrepancy Detector")
    print(f"{'='*70}\n")
    
    # Load profiles from profile_data.json
    profiles = load_test_profiles()
    
    if len(profiles) < 2:
        print("⚠ Need at least 2 profile sources. Available:", list(profiles.keys()))
        return None
    
    print(f"\n📄 Comparing {len(profiles)} profiles: {list(profiles.keys())}")
    
    # Analyze discrepancies
    result = compare_profile_sources(
        resume=profiles.get('resume'),
        linkedin=profiles.get('linkedin'),
        portfolio=profiles.get('portfolio')
    )
    
    # Print results
    print(f"\n{'='*70}")
    print("DISCREPANCY RESULTS")
    print(f"{'='*70}\n")
    
    if 'error' in result:
        print(f"⚠ Error: {result['error']}")
        return result
    
    print(f"📊 Consistency Score: {result.get('consistency_score', 0)}%\n")
    
    # NEW: Comparison Table
    comparison_table = result.get('comparison_table', [])
    if comparison_table:
        print(f"\n📊 Comparison Table ({len(comparison_table)} items):")
        print(f"{'Category':<15} {'Field':<25} {'Resume':<15} {'LinkedIn':<15} {'Portfolio':<15} {'Status':<10}")
        print("-" * 95)
        for item in comparison_table[:20]:  # Show first 20
            print(f"{item.get('category', ''):<15} {item.get('field', '')[:24]:<25} "
                  f"{(item.get('resume_value', '') or '-')[:14]:<15} "
                  f"{(item.get('linkedin_value', '') or '-')[:14]:<15} "
                  f"{(item.get('portfolio_value', '') or '-')[:14]:<15} "
                  f"{item.get('status', ''):<10}")
    
    # Mismatches
    mismatches = result.get('mismatches', [])
    if mismatches:
        print(f"\n⚠️ Mismatches ({len(mismatches)} items):")
        for item in mismatches:
            print(f"  • {item.get('field')}: R='{item.get('resume_value', '-')}' | "
                  f"L='{item.get('linkedin_value', '-')}' | P='{item.get('portfolio_value', '-')}'")
    
    # Partial presence
    partial = result.get('partial_presence', [])
    if partial:
        print(f"\n📝 Partial Presence ({len(partial)} items missing from at least one source):")
        for item in partial[:10]:
            r = "✓" if item.get('resume_value') else "✗"
            l = "✓" if item.get('linkedin_value') else "✗"
            p = "✓" if item.get('portfolio_value') else "✗"
            print(f"  • {item.get('field')}: Resume={r} | LinkedIn={l} | Portfolio={p}")
    
    # Discrepancies with severity
    discrepancies = result.get('discrepancies', [])
    if discrepancies:
        print(f"\n⚠ Detailed Discrepancies ({len(discrepancies)}):")
        for d in discrepancies:
            print(f"\n  📌 {d.get('field', 'Unknown')} [{d.get('severity', 'low').upper()}]")
            print(f"     Resume: {d.get('resume', '-')}")
            print(f"     LinkedIn: {d.get('linkedin', '-')}")
            print(f"     Portfolio: {d.get('portfolio', '-')}")
            print(f"     Issue: {d.get('issue', '')}")
    else:
        print("\n✅ No major discrepancies found!")
    
    # Skill comparison (legacy)
    skills = result.get('skill_comparison', [])
    if skills:
        print(f"\n\n💡 Skill Comparison ({len(skills)} skills):")
        print(f"{'Skill':<25} {'Resume':<10} {'LinkedIn':<10} {'Portfolio':<10}")
        print("-" * 55)
        for s in skills[:15]:
            r = "✓" if s.get('in_resume') else "✗"
            l = "✓" if s.get('in_linkedin') else "✗"
            p = "✓" if s.get('in_portfolio') else "✗"
            print(f"{s.get('skill', ''):<25} {r:<10} {l:<10} {p:<10}")
    
    # Recommendations
    recs = result.get('recommendations', [])
    if recs:
        print(f"\n💡 Recommendations:")
        for rec in recs:
            print(f"  • {rec}")
    
    # Format for table (UI)
    formatter = TableFormatter()
    table_data = formatter.format_all(result)
    
    # Save outputs
    output_dir = os.path.dirname(__file__)
    
    with open(os.path.join(output_dir, 'discrepancy_result.json'), 'w') as f:
        json.dump(result, f, indent=2)
    
    with open(os.path.join(output_dir, 'discrepancy_table.json'), 'w') as f:
        json.dump(table_data, f, indent=2)
    
    print(f"\n💾 Saved to: discrepancy_result.json, discrepancy_table.json")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    test_discrepancy()
