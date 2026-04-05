"""
Cover Letter Module - Multi-mode generation with optional context enrichment.

Modes: storyline | disruptive | regular | auto | custom
"""

from .models import CoverLetter, JDToneAnalysis, EnhancedPrompt
from .generator import CoverLetterGenerator, generate_cover_letter
from .jd_analyzer import JDToneAnalyzer, analyze_jd_tone
from .prompt_enhancer import PromptEnhancer, enhance_prompt

__all__ = [
    "CoverLetter",
    "JDToneAnalysis",
    "EnhancedPrompt",
    "CoverLetterGenerator",
    "generate_cover_letter",
    "JDToneAnalyzer",
    "analyze_jd_tone",
    "PromptEnhancer",
    "enhance_prompt",
]
