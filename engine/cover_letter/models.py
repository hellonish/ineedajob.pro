"""
Cover Letter Models - Pydantic schemas for generation, JD analysis, and prompt enhancement.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class CoverLetter(BaseModel):
    """Full cover letter output with metadata."""

    mode: str = Field(
        default="regular",
        description="Generation mode used (storyline | disruptive | regular | auto | custom)",
    )
    mode_label: str = Field(
        default="",
        description="Human-readable label, e.g. 'Auto-Detected: Storyline'",
    )
    jd_tone_detected: Optional[str] = Field(
        default=None,
        description="Detected JD tone when auto mode was used",
    )
    enhanced_prompt: Optional[str] = Field(
        default=None,
        description="The enhanced prompt used in custom mode",
    )
    company_intel_used: bool = Field(
        default=False,
        description="Whether company news / intel was included",
    )

    greeting: str = Field(default="Dear Hiring Manager,")
    body_paragraphs: List[str] = Field(
        default_factory=list,
        description="Main letter paragraphs (count varies by mode)",
    )
    closing_paragraph: str = Field(default="")
    sign_off: str = Field(default="Best regards,")

    full_letter: str = Field(default="", description="Complete formatted cover letter")


class JDToneAnalysis(BaseModel):
    """Result of analyzing a job description's tone and culture."""

    recommended_mode: str = Field(
        description="Recommended mode: storyline, disruptive, or regular",
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence (0-1)",
    )
    tone_signals: List[str] = Field(
        default_factory=list, description="Detected tone keywords from the JD",
    )
    culture_indicators: List[str] = Field(
        default_factory=list, description="Detected culture / vibe markers",
    )
    formality_level: str = Field(
        default="formal",
        description="formal | semi-formal | casual",
    )
    industry: str = Field(default="", description="Detected industry / sector")
    reasoning: str = Field(
        default="", description="Brief explanation of the recommendation",
    )


class EnhancedPrompt(BaseModel):
    """Result of enhancing a user's rough prompt."""

    enhanced_prompt: str = Field(
        description="Detailed, context-aware prompt ready for LLM consumption",
    )
    enhancements_made: List[str] = Field(
        default_factory=list, description="What was improved",
    )
    suggested_mode: str = Field(
        default="custom",
        description="Suggested generation mode based on prompt intent",
    )
