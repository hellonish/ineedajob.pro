"""
Job Module - Parse and analyze job postings.

Extracts structured data from job posting text including qualifications, skills, and keywords.
"""

from .models import JobPosting
from .parser import JobParser, parse_job_posting

__all__ = [
    'JobPosting',
    'JobParser',
    'parse_job_posting'
]
