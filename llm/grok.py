"""
xAI Grok LLM provider.

Uses the OpenAI-compatible xAI API endpoint with instructor
for structured outputs.
"""

from typing import Optional, Any

import instructor
from openai import OpenAI

from .base import BaseLLMProvider


class GrokProvider(BaseLLMProvider):
    """xAI Grok LLM provider."""

    DEFAULT_MODEL = "grok-3"
    DEFAULT_BASE_URL = "https://api.x.ai/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key=api_key, env_var="XAI_API_KEY")
        self._model = model or self.DEFAULT_MODEL
        self._base_url = base_url or self.DEFAULT_BASE_URL

    def get_client(self) -> Any:
        if self._client is None:
            api_key = self._resolve_api_key()
            self._client = instructor.from_openai(
                OpenAI(
                    base_url=self._base_url,
                    api_key=api_key,
                    timeout=60.0,
                ),
                mode=instructor.Mode.JSON,
            )
        return self._client

    @property
    def model(self) -> str:
        return self._model

    def reset(self):
        self._client = None
