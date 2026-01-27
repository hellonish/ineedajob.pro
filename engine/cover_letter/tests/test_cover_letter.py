"""Test Cover Letter Generator with Multiple Modes"""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.cover_letter import generate_cover_letter, CoverLetterGenerator


def test_cover_letter_modes():
    print(f"\n{'='*70}")
    print("Testing Cover Letter Generator - Multiple Modes")
    print(f"{'='*70}\n")
    
    # Load test data from analysis tests
    test_dir = os.path.dirname(__file__)
    analysis_test_dir = os.path.join(os.path.dirname(os.path.dirname(test_dir)), 'analysis', 'tests')
    
    with open(os.path.join(analysis_test_dir, 'job_result.json'), 'r') as f:
        job_posting = json.load(f)
    
    with open(os.path.join(analysis_test_dir, 'profile.json'), 'r') as f:
        profile_data = json.load(f)
    
    unified_profile = profile_data.get('unified_profile', {})
    
    print(f"✓ Job: {job_posting.get('job_title')}")
    print(f"✓ Applicant: {unified_profile.get('basics', {}).get('name')}")
    
    # Test a specific mode (change this to test different modes)
    mode = "concise"  # Options: professional, conversational, concise, creative, storytelling
    
    print(f"\n📝 Generating '{mode}' cover letter...")
    
    result = generate_cover_letter(
        job_posting=job_posting,
        unified_profile=unified_profile,
        mode=mode
    )
    
    # Display result
    print(f"\n{'='*70}")
    print(f"COVER LETTER ({mode.upper()} MODE)")
    print(f"{'='*70}\n")
    
    print(result.full_letter)
    
    # Save output
    output_path = os.path.join(test_dir, f'cover_letter_{mode}.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    text_path = os.path.join(test_dir, f'cover_letter_{mode}.txt')
    with open(text_path, 'w') as f:
        f.write(result.full_letter)
    
    print(f"\n💾 Saved to: cover_letter_{mode}.json, cover_letter_{mode}.txt")
    
    # Show available modes
    print(f"\n{'='*70}")
    print("AVAILABLE MODES:")
    print("  • professional - Formal, traditional corporate style")
    print("  • conversational - Friendly, approachable tone")
    print("  • concise - Brief, to-the-point (~200 words)")
    print("  • creative - Standout, unique approach")
    print("  • storytelling - Narrative-driven, engaging")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_cover_letter_modes()
