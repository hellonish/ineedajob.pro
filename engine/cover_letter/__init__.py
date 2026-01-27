"""
Cover Letter Module - Generate personalized cover letters.
"""

from .models import CoverLetter
from .generator import CoverLetterGenerator, generate_cover_letter

__all__ = [
    'CoverLetter',
    'CoverLetterGenerator',
    'generate_cover_letter'
]
