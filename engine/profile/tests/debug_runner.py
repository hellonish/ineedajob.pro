"""
Debug Runner to verify Profile Parsers on actual files.
Run with: PYTHONPATH=. python engine/profile/tests/debug_runner.py
"""

import os
import json
import asyncio
# from dotenv import load_dotenv

# load_dotenv()  # Ensure API Keys are loaded

from engine.profile import parse_resume, parse_linkedin, parse_portfolio, create_unified_profile

TEST_DIR = os.path.dirname(__file__)

def read_file_bytes(filename):
    path = os.path.join(TEST_DIR, filename)
    with open(path, 'rb') as f:
        return f.read()

def run_debug():
    print("="*60)
    print("🚀 STARTING PROFILE EXTRACTION DEBUG")
    print("="*60)

    # 1. Parse Resume
    print("\n📄 Parsing Resume (resume.pdf)...")
    try:
        resume_bytes = read_file_bytes('resume.pdf')
        resume_data = parse_resume(resume_bytes)
        print("✅ Resume Parsed successfully.")
    except Exception as e:
        print(f"❌ Resume Parsing Failed: {e}")
        resume_data = {}

    # 2. Parse LinkedIn
    print("\n🔗 Parsing LinkedIn (linkedin.pdf)...")
    try:
        linkedin_bytes = read_file_bytes('linkedin.pdf')
        linkedin_data = parse_linkedin(linkedin_bytes)
        print("✅ LinkedIn Parsed successfully.")
    except Exception as e:
        print(f"❌ LinkedIn Parsing Failed: {e}")
        linkedin_data = {}

    # 3. Parse Portfolio
    print("\n🌐 Parsing Portfolio (index.html)...")
    try:
        portfolio_bytes = read_file_bytes('index.html')
        portfolio_data = parse_portfolio(portfolio_bytes)
        print("✅ Portfolio Parsed successfully.")
    except Exception as e:
        print(f"❌ Portfolio Parsing Failed: {e}")
        portfolio_data = {}

    # 4. Unify
    print("\n🔄 Creating Unified Profile...")
    unified = create_unified_profile({
        'resume': resume_data,
        'linkedin': linkedin_data,
        'portfolio': portfolio_data
    })
    
    # OUTPUT RESULTS
    output_path = os.path.join(TEST_DIR, 'debug_output.json')
    final_output = {
        'unified_profile': unified,
        'sources': {
            'resume': resume_data,
            'linkedin': linkedin_data,
            'portfolio': portfolio_data
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"\n💾 Output saved to: {output_path}")
    
    # Print a summary
    print("\n" + "="*30)
    print("SUMMARY OF UNIFIED PROFILE")
    print("="*30)
    print(f"Name: {unified.get('basics', {}).get('name')}")
    print(f"Skills ({len(unified.get('skills', []))}): {unified.get('skills', [])[:5]}...")
    print(f"Work Experience: {len(unified.get('work_experience', []))} entries")
    if unified.get('work_experience'):
        first_job = unified['work_experience'][0]
        print(f"  Latest: {first_job.get('job_title')} at {first_job.get('company_name')}")
    
    print("\nFull JSON output is available in debug_output.json")

if __name__ == "__main__":
    run_debug()
