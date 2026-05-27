"""Profile-to-job matching module."""

from .matcher import JobMatcher, match_profile_to_job, match_profile_to_job_with_xai
from .models import (
    ActionPriority,
    ConstraintMatch,
    ConstraintStatus,
    DomainMatch,
    EvidenceItem,
    JobMatchLLMResponse,
    JobMatchRequest,
    JobMatchResult,
    JobMatchSummary,
    MatchBand,
    MatchLevel,
    ResponsibilityMatch,
    ResumeAction,
    ResumeActionType,
    ScoreComponent,
    SkillMatch,
)
from .prompts import build_job_match_messages

__all__ = [
    "ActionPriority",
    "ConstraintMatch",
    "ConstraintStatus",
    "DomainMatch",
    "EvidenceItem",
    "JobMatchLLMResponse",
    "JobMatchRequest",
    "JobMatchResult",
    "JobMatchSummary",
    "JobMatcher",
    "MatchBand",
    "MatchLevel",
    "ResponsibilityMatch",
    "ResumeAction",
    "ResumeActionType",
    "ScoreComponent",
    "SkillMatch",
    "build_job_match_messages",
    "match_profile_to_job",
    "match_profile_to_job_with_xai",
]
