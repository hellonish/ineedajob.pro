"""
JD Tone Analyzer - Analyzes a job description to recommend the best cover letter mode.

Uses the LLM to detect formality, culture signals, industry, and maps them
to one of three primary modes: storyline, disruptive, regular.
"""

import time
from typing import Dict

from engine.models import LLMClient
from .models import JDToneAnalysis

_SYSTEM_PROMPT = """\
You are an expert at reading job descriptions and determining which cover \
letter style will resonate most with the hiring team.

Analyze the job posting below and return a structured recommendation.

---

MODES - pick exactly one:

1. "storyline"
   Best for mission-driven companies, startups, roles emphasising growth, \
culture-first orgs, companies with a strong narrative.
   Signals: "on a mission", "join our journey", "passionate about", \
"make an impact", team-centric language, storytelling.

2. "disruptive"
   Best for tech-forward companies, innovative roles, companies challenging \
the status quo, cutting-edge fields.
   Signals: "disrupt", "innovate", "reimagine", "game-changer", \
"first-of-its-kind", "challenging the status quo", bold language.

3. "regular"
   Best for established corporations, formal industries (finance, legal, \
gov), structured roles, traditional cultures.
   Signals: formal requirement lists, corporate language, conservative \
terminology, structured qualifications.

---

RULES:
- Return ONLY the recommended mode ("storyline" / "disruptive" / "regular").
- Provide a confidence score (0.0 - 1.0). Be honest - if the JD is \
ambiguous, confidence should be lower.
- List 3-8 tone_signals found verbatim in the JD.
- List 2-5 culture_indicators you infer.
- Set formality_level: "formal", "semi-formal", or "casual".
- Guess the industry sector in one short phrase.
- Write a 1-2 sentence reasoning.
"""

_USER_TEMPLATE = """\
JOB TITLE: {job_title}
COMPANY: {company_name}
COMPANY ABOUT: {company_about}
JOB DESCRIPTION:
{job_description}
REQUIRED QUALIFICATIONS: {required}
TECHNICAL SKILLS: {technical}
KEYWORDS: {keywords}
"""


class JDToneAnalyzer:
    """Analyzes a JD and recommends the optimal cover letter mode."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def analyze(self, job_posting: Dict) -> JDToneAnalysis:
        """
        Args:
            job_posting: Parsed job posting dict (same shape as engine/job/models.py).

        Returns:
            JDToneAnalysis with recommended_mode and supporting evidence.
        """
        print("  Analyzing JD tone...")
        start = time.time()

        user_msg = _USER_TEMPLATE.format(
            job_title=job_posting.get("job_title", ""),
            company_name=job_posting.get("company_name", ""),
            company_about=job_posting.get("company_about", ""),
            job_description=job_posting.get("job_description", ""),
            required=job_posting.get("required_qualifications", []),
            technical=job_posting.get("technical_skills", []),
            keywords=job_posting.get("job_keywords", []),
        )

        result: JDToneAnalysis = self._llm.complete(
            response_model=JDToneAnalysis,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        print(f"  Recommended: {result.recommended_mode} "
              f"(confidence {result.confidence:.0%}, "
              f"{time.time() - start:.1f}s)")
        return result


def analyze_jd_tone(job_posting: Dict, llm: LLMClient) -> JDToneAnalysis:
    """One-shot JD tone analysis."""
    return JDToneAnalyzer(llm).analyze(job_posting)
