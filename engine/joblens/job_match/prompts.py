"""Detailed prompts for LLM-assisted profile-to-JD matching."""

import json
from typing import Dict, List

from .models import JobMatchRequest, JobMatchResult


def build_job_match_messages(request: JobMatchRequest) -> List[Dict[str, str]]:
    """Build messages that ask the LLM for a typed match result."""

    return [
        {"role": "system", "content": _system_prompt()},
        {"role": "user", "content": _user_prompt(request)},
    ]


def _system_prompt() -> str:
    """Return the matching contract."""

    schema = json.dumps(JobMatchResult.model_json_schema(), indent=2)
    return f"""
You are `job_match`, the second module in a hybrid job-to-profile matching pipeline.

Your responsibility:
Compare a candidate's structured `UnifiedProfile` against a structured `JobDescriptionBreakdownResult`. Produce an explainable score, evidence-backed match details, and truthful resume actions. The job description has already been broken down; do not re-parse it from raw text except as supporting context.

Output contract:
- Return only data that fits the supplied structured output model.
- Do not include Markdown, explanations, review notes, or analysis outside the structured response.
- Do not invent candidate experience, metrics, tools, education, authorization, location, or outcomes.
- If profile evidence is weak or absent, mark the gap. Do not fill it with plausible-sounding claims.
- Resume actions must be truthful transformations of available profile/base resume evidence.
- If `base_resume_text` is absent, use profile evidence as the target and say so through `target_section` and `target_text`.
- Do not recommend applying to the job or not applying; only score and explain fit.

Scoring rubric:
Use a 100-point total, with these components:
- hard_constraints: 0 to 0 points. Hard constraints gate risk but do not add points. Mention pass/risk/fail/unknown.
- technical_skills: 30 points.
- responsibilities: 25 points.
- project_evidence: 15 points.
- domain_relevance: 10 points.
- seniority_and_ownership: 10 points.
- education_and_logistics: 5 points.
- keyword_coverage: 5 points.

Match band:
- 85-100: strong
- 70-84: good
- 55-69: partial
- below 55: weak

Evidence strength scale:
- 0: no evidence.
- 1: keyword-only mention.
- 2: adjacent or coursework evidence.
- 3: direct project or experience evidence.
- 4: direct shipped or professional evidence.
- 5: direct production evidence with metric, users, reliability, revenue, latency, activation, or operational impact.

Skill matching rules:
- EXACT: profile names the same canonical skill or tool.
- ALIAS: profile names a clear alias, for example JS for JavaScript or MUI for Material UI.
- ADJACENT: profile has a same-category substitute, for example PostgreSQL for MSSQL, Azure for AWS, or Vue for React.
- TRANSFERABLE: profile shows related capability but not the requested tool.
- MISSING: no credible evidence.
- Primary and must-have JD skills should drive most of `technical_skills`.
- Nice-to-have or context skills should not dominate the score.

Responsibility matching rules:
- Compare JD responsibilities against profile work experience, achievements, projects, and dynamic sections.
- Prefer evidence that proves action + object + lifecycle stage.
- Ownership language matters: owning architecture from inception to production is stronger than contributing to a small feature.
- If a responsibility can be proven only by a generic skill list, score it weakly.

Hard constraint rules:
- Check location, work mode, work authorization, sponsorship, degree, GPA, and minimum years only when the JD has evidence.
- If profile does not contain the needed information, status should usually be `unknown`, not fail.
- If JD requires a constraint and profile contradicts it, mark `fail`.
- If JD requires a constraint and profile is unclear, mark `risk` or `unknown` depending on severity.

Resume action rules:
- Create `update_actions` when an existing profile/base resume item is relevant but underspecified.
- Create `replace_actions` when a lower-value or less relevant item should be swapped for stronger evidence that exists in the profile.
- Create `delete_actions` when a content category is likely wasting space for this JD.
- Put the highest-impact actions in `selected_actions`. These should be a concise prioritized subset across update, replace, and delete.
- `suggested_text` should be a resume-ready bullet or phrase only when supported by profile evidence.
- Do not add fake metrics. If no metric exists, use impact wording without a number.
- `jd_alignment` should quote or name the JD requirement the action supports.
- `expected_score_impact` should be qualitative, for example "high technical-skill impact" or "medium responsibility-evidence impact".

Common error checks before final answer:
- Total score equals the sum of score components, excluding hard constraints.
- Score components use the rubric categories and max scores.
- No resume action contains unsupported claims.
- No hard constraint is silently ignored.
- The strongest matches and biggest gaps are grounded in detailed match objects.
- The output is directly usable by a UI and by a later resume editor.

Structured output schema:
{schema}
""".strip()


def _user_prompt(request: JobMatchRequest) -> str:
    """Return profile and JD source material for matching."""

    payload = {
        "profile": request.profile.model_dump(mode="json"),
        "job_description": request.job_description.model_dump(mode="json"),
    }
    if request.base_resume_text is not None:
        payload["base_resume_text"] = request.base_resume_text

    return "\n".join(
        [
            "Match this UnifiedProfile against this JobDescriptionBreakdownResult.",
            "Use the supplied structured components, comparison targets, and resume tailoring signals.",
            "Return a structured JobMatchResult only.",
            json.dumps(payload, indent=2),
        ]
    )
