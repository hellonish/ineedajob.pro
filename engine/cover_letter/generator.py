"""
Cover Letter Generator - Multi-mode generation with optional context enrichment.

Modes:
  storyline  - Narrative arc driven by career journey.
  disruptive - Bold, unconventional, challenges the norm.
  regular    - Traditional professional - clean and polished.
  auto       - Runs JD tone analysis first, picks the best mode.
  custom     - Enhances the user's rough prompt, then generates.
"""

import time
from typing import Dict, List, Optional

from engine.models import LLMClient
from .models import CoverLetter, JDToneAnalysis, EnhancedPrompt
from .jd_analyzer import JDToneAnalyzer
from .prompt_enhancer import PromptEnhancer

MODE_PROMPTS: Dict[str, str] = {

    "storyline": """\
You are a master storyteller writing a cover letter that reads like a \
compelling short chapter - not a list of qualifications.

STRUCTURE - The Hero's Journey:

1. OPENING - Begin with a pivotal moment, defining experience, or insight \
that connects directly to this role. NOT "I am writing to apply for..." \
Drop the reader INTO a scene or realisation.

2. RISING ACTION - Show career progression through 2-3 key moments that \
build toward this opportunity. Each experience flows into the next, \
creating narrative momentum.

3. CONFLICT TO RESOLUTION - Address a challenge you overcame that is \
relevant to this company's problems. Show, don't tell. Use specific \
details, numbers, outcomes.

4. THEMATIC BRIDGE - Connect your story arc to the company's mission or \
challenges. "This is why [Company]'s mission to [X] resonates - because \
I've seen first-hand..."

5. FORWARD VISION - Close with where this story heads next - with them. \
End with confidence and specificity.

RULES:
- Every paragraph must flow naturally into the next (narrative cohesion).
- Use sensory language and specific details - not "led a team" but "guided \
a 12-person cross-functional team through..."
- The letter should read like a short essay, not bullet points.
- Reference specific experiences from the profile with context.
- Mirror the company's language and values from the JD.
- Target: 300-400 words.

Return a JSON object with these fields:
- greeting (string)
- body_paragraphs (array of 4-5 strings - the main letter content)
- closing_paragraph (string - call to action and thank you)
- sign_off (string)
- full_letter (string - the complete formatted letter with greeting, all \
paragraphs, closing, sign_off, and applicant name appended at the end)""",

    "disruptive": """\
You are writing for someone who refuses to blend in. This cover letter \
must make the hiring manager stop scrolling and think "finally, someone \
different."

APPROACH - First Principles:

1. OPEN WITH A PROVOCATION - Start with a bold observation, counterintuitive \
insight, or direct challenge related to the industry or role. \
NOT "I saw your job posting..." \
Examples:
  "Most [role]s approach [problem] wrong. Here's what I've learned..."
  "Your industry has a [problem] nobody talks about."
  "I almost didn't apply. Here's why I changed my mind."

2. VALUE THROUGH IMPACT - Don't list qualifications. Frame 2-3 key \
achievements as case studies: state the OUTCOME first, then unpack the \
thinking behind it.

3. CONNECT THROUGH THINKING - Show HOW you think, not just WHAT you've done. \
Reference your approach, philosophy, intellectual curiosity.

4. THE ASK - Flip the script. Instead of "I hope you'll consider me": \
"I'm looking for a team that's serious about [X]. If that's you, I'd \
love to talk." Confidence without arrogance.

5. CLOSE WITH A HOOK - Leave them wanting more. A final thought or question \
that invites conversation, not just an interview.

RULES:
- Never use cliches: "passionate", "team player", "hard worker", \
"detail-oriented".
- Never start with "I am writing to express my interest..."
- Challenge at least one assumption about the industry or role.
- Show intellectual confidence - say what you believe, not what they \
want to hear.
- Vary sentence length for rhythm: short punches mixed with longer ones.
- Bold claims need bold evidence - be specific with numbers and outcomes.
- Target: 250-350 words. Be memorable, not long-winded.

Return a JSON object with these fields:
- greeting (string)
- body_paragraphs (array of 4-5 strings - the main letter content)
- closing_paragraph (string - call to action)
- sign_off (string)
- full_letter (string - the complete formatted letter with greeting, all \
paragraphs, closing, sign_off, and applicant name appended at the end)""",

    "regular": """\
You are writing a polished, traditional cover letter that demonstrates \
competence, clear communication, and genuine interest.

STRUCTURE:

1. OPENING - State the role and a concise hook about your fit. \
"I'm excited to apply for [Role] at [Company] - my [X] years of \
experience in [domain] align directly with your need for [key req]."

2. EXPERIENCE - Connect 2-3 specific experiences to the role's \
requirements. Use the pattern: "At [Company], I [action] -> [result]." \
Reference quantifiable outcomes where possible.

3. SKILLS ALIGNMENT - Map your technical and soft skills to what the \
job requires. Don't list - show them in context.

4. COMPANY INTEREST - Reference something specific about the company \
(mission, product, recent news, values) and connect it to your \
motivation.

5. CLOSING - Express enthusiasm, mention availability, thank them. \
"I would welcome the opportunity to discuss how my background in [X] \
can contribute to [Company]'s [specific goal/project]."

RULES:
- Be genuine and specific - no generic praise.
- Reference actual experiences from the profile, not invented ones.
- Mirror keywords from the JD naturally - do not keyword-stuff.
- Maintain a formal but warm tone.
- Target: 300-400 words.

Return a JSON object with these fields:
- greeting (string)
- body_paragraphs (array of 4-5 strings - the main letter content)
- closing_paragraph (string - call to action and thank you)
- sign_off (string)
- full_letter (string - the complete formatted letter with greeting, all \
paragraphs, closing, sign_off, and applicant name appended at the end)""",
}

MODE_TEMPERATURES = {
    "storyline": 0.8,
    "disruptive": 0.85,
    "regular": 0.6,
    "custom": 0.75,
}


class CoverLetterGenerator:
    """
    Multi-mode cover letter generator.

    Receives an LLMClient via injection. The API layer creates the client
    based on the user's model preference and passes it here.
    """

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def generate(
        self,
        job_posting: Dict,
        unified_profile: Dict,
        mode: str = "regular",
        applicant_name: Optional[str] = None,
        hiring_manager: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        company_news: Optional[List[Dict]] = None,
        company_intel: Optional[str] = None,
    ) -> CoverLetter:
        """
        Generate a cover letter.

        Args:
            job_posting:      Parsed job posting dict.
            unified_profile:  Complete applicant profile dict.
            mode:             One of storyline, disruptive, regular, auto, custom.
            applicant_name:   Override name from profile.
            hiring_manager:   Hiring manager name if known.
            custom_prompt:    Rough user prompt (used with mode="custom").
            company_news:     List of news article dicts for context enrichment.
            company_intel:    Free-text company intel / about section.

        Returns:
            CoverLetter with metadata, structured paragraphs, and full_letter.
        """
        print(f"Generating cover letter (mode: {mode})...")
        start = time.time()

        applicant_name = applicant_name or unified_profile.get("basics", {}).get("name", "Applicant")

        actual_mode = mode
        jd_tone: Optional[JDToneAnalysis] = None
        if mode == "auto":
            jd_tone = JDToneAnalyzer(self._llm).analyze(job_posting)
            actual_mode = jd_tone.recommended_mode

        enhanced: Optional[EnhancedPrompt] = None
        if mode == "custom" and custom_prompt:
            enhanced = PromptEnhancer(self._llm).enhance(
                custom_prompt, job_posting, unified_profile,
            )

        context = self._build_context(
            job_posting, unified_profile, applicant_name,
            hiring_manager, company_news, company_intel,
        )

        system_prompt = self._resolve_system_prompt(actual_mode, enhanced)

        temperature = MODE_TEMPERATURES.get(actual_mode, 0.7)
        result = self._llm.complete(
            response_model=CoverLetter,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a cover letter:\n\n{context}"},
            ],
            temperature=temperature,
            max_tokens=4096,
        )

        result.mode = actual_mode
        result.company_intel_used = bool(company_news or company_intel)

        if jd_tone:
            result.jd_tone_detected = jd_tone.recommended_mode
            result.mode_label = f"Auto-Detected: {jd_tone.recommended_mode.title()}"

        if enhanced:
            result.enhanced_prompt = enhanced.enhanced_prompt

        if not result.full_letter:
            result.full_letter = self._format_full_letter(result, applicant_name)

        print(f"Cover letter generated ({actual_mode}) in {time.time() - start:.1f}s")
        return result

    def _build_context(
        self,
        job_posting: Dict,
        unified_profile: Dict,
        applicant_name: str,
        hiring_manager: Optional[str],
        company_news: Optional[List[Dict]],
        company_intel: Optional[str],
    ) -> str:
        parts = [
            f"APPLICANT NAME: {applicant_name}",
            f"HIRING MANAGER: {hiring_manager or 'Unknown'}",
            "",
            "JOB POSTING:",
            f"- Title: {job_posting.get('job_title', 'Unknown')}",
            f"- Company: {job_posting.get('company_name', 'Unknown')}",
            f"- About Company: {job_posting.get('company_about', '')}",
            f"- Description: {job_posting.get('job_description', '')}",
            f"- Required Qualifications: {job_posting.get('required_qualifications', [])}",
            f"- Technical Skills: {job_posting.get('technical_skills', [])}",
            f"- Soft Skills: {job_posting.get('soft_skills', [])}",
            f"- Keywords: {job_posting.get('job_keywords', [])}",
        ]

        if company_intel:
            parts += ["", "COMPANY INTELLIGENCE:", company_intel]

        if company_news:
            company = job_posting.get("company_name", "the company")
            articles = "\n".join(
                f"- [{a.get('source', '?')}] {a.get('title', '')}: "
                f"{a.get('description', '')}"
                for a in company_news[:5]
            )
            parts += [
                "",
                f"RECENT NEWS ABOUT {company}:",
                articles,
                "",
                "INSTRUCTION: Reference 1-2 relevant news items naturally to "
                "demonstrate genuine awareness of the company's current activities.",
            ]

        parts += ["", "APPLICANT PROFILE:", str(unified_profile)]
        return "\n".join(parts)

    def _resolve_system_prompt(
        self, mode: str, enhanced: Optional[EnhancedPrompt],
    ) -> str:
        if enhanced:
            return (
                "You are a professional cover letter writer.\n\n"
                f"FOLLOW THESE INSTRUCTIONS PRECISELY:\n{enhanced.enhanced_prompt}\n\n"
                "OUTPUT FORMAT - return a JSON object with these fields:\n"
                "- greeting (string)\n"
                "- body_paragraphs (array of strings - the main letter content)\n"
                "- closing_paragraph (string - call to action)\n"
                "- sign_off (string)\n"
                "- full_letter (string - the complete formatted letter with "
                "greeting, paragraphs, closing, sign_off, and applicant name appended)"
            )
        return MODE_PROMPTS.get(mode, MODE_PROMPTS["regular"])

    @staticmethod
    def _format_full_letter(letter: CoverLetter, applicant_name: str) -> str:
        parts: List[str] = [letter.greeting, ""]
        for para in letter.body_paragraphs:
            parts.extend([para, ""])
        parts.extend([
            letter.closing_paragraph,
            "",
            letter.sign_off,
            applicant_name,
        ])
        return "\n".join(parts)


def generate_cover_letter(
    job_posting: Dict,
    unified_profile: Dict,
    llm: LLMClient,
    mode: str = "regular",
    applicant_name: Optional[str] = None,
    hiring_manager: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    company_news: Optional[List[Dict]] = None,
    company_intel: Optional[str] = None,
) -> CoverLetter:
    """One-shot cover letter generation."""
    return CoverLetterGenerator(llm).generate(
        job_posting=job_posting,
        unified_profile=unified_profile,
        mode=mode,
        applicant_name=applicant_name,
        hiring_manager=hiring_manager,
        custom_prompt=custom_prompt,
        company_news=company_news,
        company_intel=company_intel,
    )
