"""DeepSeek chat client (OpenAI-compatible API).

Uses the OpenAI SDK with DeepSeek base URL and DEEPSEEK_API_KEY. Implements
BaseLlmClient (generate, generate_structured); same as OpenAIClient, different config.
"""

import json
import os
from typing import Any

from openai import OpenAI

from llm.base import BaseLlmClient, Message


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


class DeepSeekClient(BaseLlmClient):
    """DeepSeek chat completions via the OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEEPSEEK_BASE_URL,
        default_model: str = DEFAULT_DEEPSEEK_MODEL,
    ) -> None:
        """Build DeepSeek client. Uses DEEPSEEK_API_KEY if api_key is None."""
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self._client = OpenAI(api_key=key, base_url=base_url)
        self._default_model = default_model

    def generate(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call chat.completions.create against DeepSeek and return assistant text."""
        model = model or self._default_model
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        choice = response.choices[0] if response.choices else None
        if not choice or not choice.message:
            return ""
        return choice.message.content or ""

    def generate_structured(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call chat.completions.create with response_format json_object; return parsed dict."""
        model = model or self._default_model
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            **kwargs,
        )
        choice = response.choices[0] if response.choices else None
        raw = (choice.message.content or "") if choice and choice.message else ""
        return json.loads(raw) if raw else {}
