"""
Profile Engine Module.

Exposes specific parsers for each source type.
"""

from .parsers import ResumeParser, LinkedInParser, PortfolioParser
from .unifier import create_unified_profile
from .models import HybridResume
from typing import Dict, Any

def parse_resume(file_content: bytes) -> Dict[str, Any]:
    parser = ResumeParser()
    result = parser.parse(file_content)
    return result.to_dict()

def parse_linkedin(file_content: bytes) -> Dict[str, Any]:
    parser = LinkedInParser()
    result = parser.parse(file_content)
    return result.to_dict()

def parse_portfolio(file_content: bytes) -> Dict[str, Any]:
    parser = PortfolioParser()
    result = parser.parse(file_content)
    return result.to_dict()

__all__ = [
    "parse_resume", 
    "parse_linkedin", 
    "parse_portfolio", 
    "create_unified_profile",
    "HybridResume"
]
