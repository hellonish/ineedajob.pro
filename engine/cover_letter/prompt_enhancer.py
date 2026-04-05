"""
Prompt Enhancer - Transforms a rough user prompt into a detailed, context-aware
generation prompt that produces a much better cover letter.
"""

import time
from typing import Dict

from engine.models import LLMClient
from .models import EnhancedPrompt

_SYSTEM_PROMPT = """\
You are a prompt engineer who specialises in cover-letter generation.

Given:
1. A USER'S ROUGH PROMPT - their intent in casual / shorthand language.
2. A JOB POSTING - the role they are applying for.
3. Their APPLICANT PROFILE - resume, skills, experience.

Your job: rewrite the rough prompt into a DETAILED, SELF-CONTAINED prompt \
that will produce an outstanding cover letter when fed to an LLM.

Enhancement checklist:
- Translate vague requests ("make it sound confident") into specific \
writing instructions ("use active voice, lead with outcomes, avoid \
hedging language").
- Reference 2-3 SPECIFIC experiences from the profile that match the \
user's intent and the job requirements.
- Incorporate relevant details from the job posting (role title, key \
requirements, company mission).
- Add tone, structure, and pacing guidance.
- Specify what to EMPHASISE and what to downplay.
- Set a target word count.
- Make the enhanced prompt self-contained - it should produce an \
excellent letter even without any other system prompt.

Do NOT write the cover letter itself. Write only the enhanced prompt.
"""

_USER_TEMPLATE = """\
ROUGH USER PROMPT:
{rough_prompt}

---
JOB POSTING:
Title: {job_title}
Company: {company_name}
About: {company_about}
Description: {job_description}
Required: {required}
Technical Skills: {technical}
Soft Skills: {soft}
Keywords: {keywords}

---
APPLICANT PROFILE:
{profile}
"""


class PromptEnhancer:
    """Enhances rough user prompts into detailed generation instructions."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def enhance(
        self,
        rough_prompt: str,
        job_posting: Dict,
        unified_profile: Dict,
    ) -> EnhancedPrompt:
        """
        Args:
            rough_prompt: User's shorthand prompt (e.g. "make it bold, mention startup").
            job_posting: Parsed JD dict.
            unified_profile: Full applicant profile dict.

        Returns:
            EnhancedPrompt with the improved prompt and metadata.
        """
        print("  Enhancing custom prompt...")
        start = time.time()

        user_msg = _USER_TEMPLATE.format(
            rough_prompt=rough_prompt,
            job_title=job_posting.get("job_title", ""),
            company_name=job_posting.get("company_name", ""),
            company_about=job_posting.get("company_about", ""),
            job_description=job_posting.get("job_description", ""),
            required=job_posting.get("required_qualifications", []),
            technical=job_posting.get("technical_skills", []),
            soft=job_posting.get("soft_skills", []),
            keywords=job_posting.get("job_keywords", []),
            profile=unified_profile,
        )

        result: EnhancedPrompt = self._llm.complete(
            response_model=EnhancedPrompt,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.5,
            max_tokens=2048,
        )

        print(f"  Enhanced in {time.time() - start:.1f}s "
              f"(suggested mode: {result.suggested_mode})")
        return result


def enhance_prompt(
    rough_prompt: str,
    job_posting: Dict,
    unified_profile: Dict,
    llm: LLMClient,
) -> EnhancedPrompt:
    """One-shot prompt enhancement."""
    return PromptEnhancer(llm).enhance(rough_prompt, job_posting, unified_profile)
