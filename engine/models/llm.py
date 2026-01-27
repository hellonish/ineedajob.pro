"""
Centralized LLM model configurations.

Provides DeepSeek and Gemini clients with API key management.
"""

import os
from typing import Optional
import instructor
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMModels:
    """Centralized LLM model manager."""
    
    _deepseek_client = None
    _gemini_client = None
    
    @classmethod
    def get_deepseek(cls, api_key: Optional[str] = None):
        """
        Get DeepSeek client with instructor for structured outputs.
        
        Args:
            api_key: Optional API key (defaults to DEEPSEEK_API_KEY env var)
            
        Returns:
            Instructor-wrapped OpenAI client configured for DeepSeek
        """
        if cls._deepseek_client is None:
            api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError(
                    "DEEPSEEK_API_KEY not found. Set it in .env file or pass as parameter."
                )
            
            cls._deepseek_client = instructor.from_openai(
                OpenAI(
                    base_url="https://api.deepseek.com",
                    api_key=api_key,
                    timeout=60.0  # 60 second timeout
                ),
                mode=instructor.Mode.JSON
            )
        
        return cls._deepseek_client
    
    @classmethod
    def get_gemini(cls, api_key: Optional[str] = None):
        """
        Get Gemini client with instructor for structured outputs.
        
        Args:
            api_key: Optional API key (defaults to GEMINI_API_KEY env var)
            
        Returns:
            Instructor-wrapped OpenAI client configured for Gemini
        """
        if cls._gemini_client is None:
            api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Set it in .env file or pass as parameter."
                )
            
            # Gemini via OpenAI-compatible endpoint
            cls._gemini_client = instructor.from_openai(
                OpenAI(
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    api_key=api_key
                ),
                mode=instructor.Mode.JSON
            )
        
        return cls._gemini_client
    
    @classmethod
    def reset(cls):
        """Reset cached clients (useful for testing)."""
        cls._deepseek_client = None
        cls._gemini_client = None


# Convenience functions
def get_deepseek_client(api_key: Optional[str] = None):
    """Get DeepSeek client."""
    return LLMModels.get_deepseek(api_key)


def get_gemini_client(api_key: Optional[str] = None):
    """Get Gemini client."""
    return LLMModels.get_gemini(api_key)
