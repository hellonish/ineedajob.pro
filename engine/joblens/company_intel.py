"""
JobLens Company Intelligence

Analyzes a company using their website content and available context.
Uses trafilatura to fetch and extract website content, then LLM to analyze.
"""

import logging
from typing import Optional, List
import trafilatura
from engine.models.llm import LLMClient
from .models import CompanyIntel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a company research analyst helping a job applicant prepare for their application and interviews.

Given information about a company (from their website, job description context, and any additional notes), provide comprehensive intelligence.

Rules:
1. Be factual — base your analysis on the provided content. If information isn't available, say "Unknown" or "Not available from provided sources".
2. For engineering culture: infer from tech blog posts, job descriptions, and any engineering team pages.
3. For interview process: provide what you can infer. Note if this is based on general knowledge vs specific data.
4. For competitors: name actual companies in the same space.
5. Talking points: these should be SPECIFIC to this company — reference their actual products, tech, values.
6. Watch outs: be honest about any concerns.
7. For ai_verdict: provide a comprehensive assessment including:
   - Overall opportunity quality (for an engineer)
   - What makes this company interesting or concerning
   - How to position yourself in the application
   - Key things to research further
   - Red/green flags synthesis

Do NOT hallucinate facts. If you don't have info, say so explicitly."""


def _fetch_website_content(url: str) -> Optional[str]:
    """Fetch and extract text content from a URL using trafilatura."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning(f"Could not fetch URL: {url}")
            return None
        extracted = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        return extracted
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def _fetch_multiple_pages(base_url: str) -> str:
    """Try to fetch key pages from a company website."""
    pages_to_try = [
        "",           # homepage
        "/about",
        "/careers",
        "/engineering",
        "/blog",
        "/team",
    ]

    # Normalize base URL
    base = base_url.rstrip("/")

    all_content = []
    for page in pages_to_try:
        url = f"{base}{page}"
        content = _fetch_website_content(url)
        if content:
            all_content.append(f"--- Page: {url} ---\n{content}")
            # Limit total content to avoid token explosion
            total = "\n\n".join(all_content)
            if len(total) > 15000:
                break

    return "\n\n".join(all_content) if all_content else ""


class CompanyIntelAnalyzer:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def analyze(
        self,
        company_name: str,
        company_website: Optional[str] = None,
        jd_context: Optional[str] = None,
        additional_notes: Optional[str] = None,
    ) -> CompanyIntel:
        """Analyze a company and return structured intelligence.

        Args:
            company_name: Name of the company
            company_website: URL of company website (will be scraped)
            jd_context: Job description text for additional context
            additional_notes: Any additional notes from the user
        """
        context_parts = [f"COMPANY: {company_name}"]

        # Fetch website content
        if company_website:
            logger.info(f"Fetching website content from {company_website}")
            website_content = _fetch_multiple_pages(company_website)
            if website_content:
                context_parts.append(f"\nWEBSITE CONTENT:\n{website_content}")
            else:
                context_parts.append("\nWEBSITE CONTENT: Could not fetch website content.")

        if jd_context:
            context_parts.append(f"\nJOB DESCRIPTION CONTEXT:\n{jd_context}")

        if additional_notes:
            context_parts.append(f"\nADDITIONAL NOTES:\n{additional_notes}")

        context = "\n".join(context_parts)

        logger.info(f"Analyzing company: {company_name}")
        result = self.llm.complete(
            response_model=CompanyIntel,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this company for a job applicant:\n\n{context}"},
            ],
            temperature=0.4,
            max_tokens=4096,
        )
        logger.info(f"Company intel generated for {company_name}")
        return result


def analyze_company(
    company_name: str,
    llm: LLMClient,
    company_website: Optional[str] = None,
    jd_context: Optional[str] = None,
    additional_notes: Optional[str] = None,
) -> CompanyIntel:
    """Convenience function."""
    return CompanyIntelAnalyzer(llm).analyze(company_name, company_website, jd_context, additional_notes)
