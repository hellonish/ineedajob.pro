"""LLM-only job description breakdown into normalized matching components."""

from typing import Any, Optional

from engine.utils import dedupe_warning_strings

from .models import (
    JobDescriptionBreakdownLLMResponse,
    JobDescriptionBreakdownResult,
    JobDescriptionInput,
)
from .prompts import build_job_description_breakdown_messages


class JobDescriptionBreaker:
    """Create normalized job description components with a structured LLM."""

    def __init__(self, llm: Any):
        """Initialize with a required structured-output LLM client."""

        if llm is None:
            raise ValueError("Job description breakdown requires an LLM client. Use XAIStructuredClient for X.AI.")
        self.llm = llm

    def break_down(self, job_text: str, source_id: Optional[str] = None) -> JobDescriptionBreakdownResult:
        """Break down a raw job description into typed matching components."""

        if not job_text or not job_text.strip():
            raise ValueError("Job description text cannot be empty.")

        job_input = JobDescriptionInput(text=job_text, source_id=source_id)
        response = self.llm.complete(
            response_model=JobDescriptionBreakdownLLMResponse,
            messages=build_job_description_breakdown_messages(job_input),
            temperature=0.0,
            max_tokens=18000,
        )
        return JobDescriptionBreakdownResult(
            input=job_input,
            breakdown=response.breakdown,
            warnings=dedupe_warning_strings(response.warnings),
        )


def break_down_job_description(
    job_text: str,
    llm: Any,
    source_id: Optional[str] = None,
) -> JobDescriptionBreakdownResult:
    """Break down a job description using the supplied structured LLM."""

    return JobDescriptionBreaker(llm).break_down(job_text=job_text, source_id=source_id)
