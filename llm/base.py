"""
Abstract base class for LLM providers.

All LLM providers (DeepSeek, Gemini, Grok, etc.) should inherit from
BaseLLMProvider and implement the get_client() method.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM provider wrappers."""

    def __init__(self, api_key: Optional[str] = None, env_var: str = ""):
        self._api_key = api_key
        self._env_var = env_var
        self._client = None

    @abstractmethod
    def get_client(self) -> Any:
        """
        Return the instructor-wrapped OpenAI client for this provider.

        Raises:
            ValueError: If no API key is available.
        """
        ...

    def _resolve_api_key(self) -> str:
        import os
        from dotenv import load_dotenv

        load_dotenv()

        key = self._api_key or os.getenv(self._env_var, "")
        if not key:
            raise ValueError(
                f"{self._env_var} not found. "
                f"Set it in .env file or pass api_key to the constructor."
            )
        return key
