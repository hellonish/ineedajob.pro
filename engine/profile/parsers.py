"""
Profile Parsers - Consolidated Logic with Base Class.
"""

import os
import fitz  # PyMuPDF
import trafilatura
from typing import Optional
from engine.models import get_deepseek_client
from .models import HybridResume
from .prompts import RESUME_PROMPT, LINKEDIN_PROMPT, PORTFOLIO_PROMPT

# ============================================================================
# BASE PARSER
# ============================================================================

class BaseProfileParser:
    """
    Base class for all profile parsers.
    Handles Client initialization and LLM interaction.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with DeepSeek client."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key required.")
        self.client = get_deepseek_client(self.api_key)

    def _parse_with_llm(self, text_content: str, system_prompt: str) -> HybridResume:
        """
        Common method to parse extracted text using DeepSeek and Pydantic model.
        """
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                response_model=HybridResume,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_content}
                ],
                temperature=0.0
            )
            return response
        except Exception as e:
            # Get class name for better error message
            parser_name = self.__class__.__name__
            raise RuntimeError(f"{parser_name} failed: {str(e)}")


# ============================================================================
# CONCRETE PARSERS
# ============================================================================

class ResumeParser(BaseProfileParser):
    """Parses PDF Resumes."""
    
    def parse(self, file_content: bytes) -> HybridResume:
        text = self._extract_pdf(file_content)
        return self._parse_with_llm(text, RESUME_PROMPT)

    def _extract_pdf(self, file_content: bytes) -> str:
        text = ""
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
        return text


class LinkedInParser(BaseProfileParser):
    """Parses PDF LinkedIn Exports."""
    
    def parse(self, file_content: bytes) -> HybridResume:
        text = self._extract_pdf(file_content)
        return self._parse_with_llm(text, LINKEDIN_PROMPT)

    def _extract_pdf(self, file_content: bytes) -> str:
        text = ""
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
        return text


class PortfolioParser(BaseProfileParser):
    """Parses HTML Portfolios."""
    
    def parse(self, file_content: bytes) -> HybridResume:
        text = self._extract_html(file_content)
        return self._parse_with_llm(text, PORTFOLIO_PROMPT)

    def _extract_html(self, file_content: bytes) -> str:
        html_string = file_content.decode('utf-8')
        extracted = trafilatura.extract(html_string)
        if not extracted:
            raise ValueError("Could not extract content from HTML")
        return extracted
