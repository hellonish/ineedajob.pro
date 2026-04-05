"""
Unit Tests for Profile Parsers (Mocked).
"""

import unittest
from unittest.mock import MagicMock, patch
from engine.profile.parsers import ResumeParser, LinkedInParser, PortfolioParser
from engine.profile.models import HybridResume, Basics, ContactInfo, WorkExperienceItem

# Sample Mock Response
MOCK_RESUME_DATA = HybridResume(
    basics=Basics(
        name="Test User",
        contact_info=ContactInfo(email="test@example.com")
    ),
    work_experience=[
        WorkExperienceItem(
            job_title="Developer",
            company_name="Tech Corp",
            start_date="2023-01",
            is_current=True
        )
    ],
    skills=["Python"],
    education=[],
    dynamic_sections={}
)

class TestParsers(unittest.TestCase):
    
    @patch('engine.profile.parsers.get_deepseek_client')
    @patch('engine.profile.parsers.fitz.open')
    def test_resume_parser(self, mock_fitz, mock_get_client):
        # Mock LLM Client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = MOCK_RESUME_DATA
        
        # Mock PDF Extraction
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Resume Text Content"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.return_value.__enter__.return_value = mock_doc
        
        # Test
        parser = ResumeParser(api_key="fake-key")
        result = parser.parse(b"fake-pdf-bytes")
        
        # Verify
        assert result.basics.name == "Test User"
        assert result.work_experience[0].company_name == "Tech Corp"
        
        # Verify LLM call
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs['response_model'] == HybridResume
        assert "Resume Text Content" in str(kwargs['messages'])

    @patch('engine.profile.parsers.get_deepseek_client')
    @patch('engine.profile.parsers.fitz.open')
    def test_linkedin_parser(self, mock_fitz, mock_get_client):
        # Setup similar mock for LinkedIn
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = MOCK_RESUME_DATA
        
        # Mock PDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "LinkedIn PDF Text"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.return_value.__enter__.return_value = mock_doc
        
        parser = LinkedInParser(api_key="fake-key")
        result = parser.parse(b"fake-bytes")
        
        assert result.basics.name == "Test User"
        # Verify correct prompt was used (implicit in code, but we can verify text reached LLM)
        mock_client.chat.completions.create.assert_called_once()

    @patch('engine.profile.parsers.get_deepseek_client')
    @patch('engine.profile.parsers.trafilatura.extract')
    def test_portfolio_parser(self, mock_extract, mock_get_client):
        # Mock LLM
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = MOCK_RESUME_DATA
        
        # Mock HTML extraction
        mock_extract.return_value = "Extracted HTML Text"
        
        parser = PortfolioParser(api_key="fake-key")
        result = parser.parse(b"<html>...</html>")
        
        assert result.basics.name == "Test User"
        mock_extract.assert_called_once()
        mock_client.chat.completions.create.assert_called_once()

if __name__ == "__main__":
    unittest.main()
