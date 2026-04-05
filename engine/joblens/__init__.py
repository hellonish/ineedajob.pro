"""
JobLens Engine Module - 6-step job application intelligence pipeline.

Steps:
1. Extract Profile - Parse and structure candidate profile
2. Parse JD - Analyze job description into structured fields
3. Company Intel - Research company from website and available data
4. Match Analysis - Compare profile vs JD with scoring
5. Contact Strategy - Who to reach out to and how
6. Action Plan - Concrete steps to maximize application success
"""

from .models import (
    ExtractedProfile, TechnicalSkills, KeyExperience, NotableProject,
    ParsedJD,
    CompanyIntel,
    MatchAnalysis, StrengthItem, GapItem,
    ContactStrategy, ContactTarget,
    ActionPlan, ResumeEdit, CoverLetterPlan, InterviewTopic, FollowUpStep,
)
from .profile_extractor import ProfileExtractor, extract_profile
from .jd_parser import JDParser, parse_jd
from .company_intel import CompanyIntelAnalyzer, analyze_company
from .match_analyzer import MatchAnalyzer, analyze_match
from .contact_finder import ContactFinder, find_contacts
from .action_planner import ActionPlanner, plan_actions

__all__ = [
    # Models
    "ExtractedProfile", "TechnicalSkills", "KeyExperience", "NotableProject",
    "ParsedJD",
    "CompanyIntel",
    "MatchAnalysis", "StrengthItem", "GapItem",
    "ContactStrategy", "ContactTarget",
    "ActionPlan", "ResumeEdit", "CoverLetterPlan", "InterviewTopic", "FollowUpStep",
    # Functions
    "extract_profile", "parse_jd", "analyze_company", "analyze_match", "find_contacts", "plan_actions",
    # Classes
    "ProfileExtractor", "JDParser", "CompanyIntelAnalyzer", "MatchAnalyzer", "ContactFinder", "ActionPlanner",
]
