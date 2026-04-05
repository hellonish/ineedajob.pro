"""Test Qualification Check"""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.analysis.qualification_check import QualificationChecker


def test_qualification_check():
    print(f"\n{'='*70}")
    print("Testing Qualification Check")
    print(f"{'='*70}\n")
    
    # Load test data
    test_dir = os.path.dirname(__file__)
    
    with open(os.path.join(test_dir, 'job_result.json'), 'r') as f:
        job_posting = json.load(f)
    
    with open(os.path.join(test_dir, 'profile.json'), 'r') as f:
        profile_data = json.load(f)
    
    resume = profile_data.get('sources', {}).get('resume', profile_data.get('unified_profile', {}))
    
    print("✓ Loaded job posting and resume")
    
    # Run check
    checker = QualificationChecker()
    result = checker.check(job_posting, resume)
    
    # Display results
    print(f"\n{'='*70}")
    print("QUALIFICATION CHECK RESULTS")
    print(f"{'='*70}\n")
    
    print(f"📌 Required Qualifications: {result.required_match_count}/{result.required_total}")
    for q in result.required_qualifications:
        status = "✓" if q.matched else "✗"
        print(f"  {status} {q.qualification[:60]}...")
        if q.matched and q.evidence:
            print(f"      Evidence: {q.evidence[:50]}...")
    
    print(f"\n💻 Technical Skills: {result.technical_match_count}/{result.technical_total}")
    for q in result.technical_skills:
        status = "✓" if q.matched else "✗"
        print(f"  {status} {q.qualification}")
    
    print(f"\n🤝 Soft Skills: {result.soft_match_count}/{result.soft_total}")
    for q in result.soft_skills:
        status = "✓" if q.matched else "✗"
        print(f"  {status} {q.qualification}")
    
    # Save output
    output_path = os.path.join(test_dir, 'qualification_check_result.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    print(f"\n💾 Saved to: qualification_check_result.json")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_qualification_check()
