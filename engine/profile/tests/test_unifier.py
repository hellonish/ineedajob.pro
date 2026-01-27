"""
Tests for Unified Profile Logic.
"""

import pytest
from engine.profile.unifier import create_unified_profile

def test_merge_basics():
    sources = {
        'resume': {
            'basics': {
                'name': 'John Doe',
                'contact_info': {'email': 'john@resume.com'}
            }
        },
        'linkedin': {
            'basics': {
                'name': 'John Doe',
                'contact_info': {'email': 'john@linkedin.com', 'linkedin_url': 'http://linkedin.com/john'}
            }
        }
    }
    
    result = create_unified_profile(sources)
    
    # Check Resume priority for email
    assert result['basics']['contact_info']['email'] == 'john@resume.com'
    # Check LinkedIn enrichment
    assert result['basics']['contact_info']['linkedin_url'] == 'http://linkedin.com/john'

def test_merge_skills():
    sources = {
        'resume': {'skills': ['Python', 'SQL']},
        'linkedin': {'skills': ['SQL', 'Docker']},
        'portfolio': {'skills': ['React']}
    }
    
    result = create_unified_profile(sources)
    
    # Check Union
    assert set(result['skills']) == {'Python', 'SQL', 'Docker', 'React'}

def test_merge_work_experience():
    sources = {
        'resume': {
            'work_experience': [
                {'company_name': 'Google', 'job_title': 'SE', 'start_date': '2022-01'}
            ]
        },
        'linkedin': {
            'work_experience': [
                {'company_name': 'Facebook', 'job_title': 'Intern', 'start_date': '2021-06'},
                {'company_name': 'Google', 'job_title': 'SE', 'start_date': '2022-01'} # Duplicate
            ]
        }
    }
    
    result = create_unified_profile(sources)
    
    # Check ordering and deduplication logic (if any implemented, currently manual dedup in code?)
    # The code implements simplistic dedup: based on (company, title) signature.
    # Resume is first, so it keeps Google/SE. LinkedIn has Google/SE too -> skipped. LinkedIn has Facebook -> added.
    
    assert len(result['work_experience']) == 2
    # Sorted by date desc
    assert result['work_experience'][0]['company_name'] == 'Google'
    assert result['work_experience'][1]['company_name'] == 'Facebook'
