"""
Test Job Posting Parser
"""

import json
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.job import JobParser, parse_job_posting


def test_job_parser():
    """Test job posting parsing with the sample job posting."""
    print(f"\n{'='*70}")
    print("Testing Job Posting Parser")
    print(f"{'='*70}\n")
    
    # Load job posting
    test_dir = os.path.dirname(__file__)
    job_file = os.path.join(test_dir, 'job_posting.txt')
    
    if not os.path.exists(job_file):
        print(f"⚠ Job posting not found at {job_file}")
        return None
    
    print(f"✓ Loading job posting from {job_file}")
    
    # Parse job posting
    try:
        parser = JobParser()
        result = parser.parse_file(job_file)
    except Exception as e:
        print(f"⚠ Error: {e}")
        return None
    
    # Print results
    print(f"\n{'='*70}")
    print("JOB PARSING RESULTS")
    print(f"{'='*70}\n")
    
    print(f"📋 Job Title: {result.job_title}")
    print(f"🏢 Company: {result.company_name}")
    print(f"📍 Location: {result.location}")
    print(f"💼 Experience Level: {result.experience_level}")
    
    print(f"\n📖 About Company:")
    print(f"  {result.company_about[:200]}..." if len(result.company_about) > 200 else f"  {result.company_about}")
    
    print(f"\n📝 Job Description:")
    print(f"  {result.job_description[:200]}..." if len(result.job_description) > 200 else f"  {result.job_description}")
    
    print(f"\n💰 Salary Range: {result.salary_range}")
    
    print(f"\n🎁 Benefits ({len(result.compensation_and_benefits)}):")
    for benefit in result.compensation_and_benefits:
        print(f"  • {benefit}")
    
    print(f"\n📌 Required Qualifications ({len(result.required_qualifications)}):")
    for qual in result.required_qualifications:
        print(f"  • {qual}")
    
    print(f"\n⭐ Preferred Qualifications ({len(result.preferred_qualifications)}):")
    for qual in result.preferred_qualifications:
        print(f"  • {qual}")
    
    print(f"\n💻 Technical Skills ({len(result.technical_skills)}):")
    for skill in result.technical_skills:
        print(f"  • {skill}")
    
    print(f"\n🤝 Soft Skills ({len(result.soft_skills)}):")
    for skill in result.soft_skills:
        print(f"  • {skill}")
    
    print(f"\n🔑 Job Keywords ({len(result.job_keywords)}):")
    for kw in result.job_keywords:
        print(f"  • {kw}")
    
    print(f"\n📝 Responsibilities ({len(result.responsibilities)}):")
    for resp in result.responsibilities[:5]:  # Show first 5
        print(f"  • {resp[:80]}...")
    
    # Save output
    result_dict = result.model_dump()
    output_path = os.path.join(test_dir, 'job_result.json')
    
    with open(output_path, 'w') as f:
        json.dump(result_dict, f, indent=2)
    
    print(f"\n💾 Saved to: job_result.json")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    test_job_parser()
