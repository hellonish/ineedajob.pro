"""OpenAI chat completion client.

Uses the official OpenAI SDK to call chat.completions.create(). Depends on
OPENAI_API_KEY. Implements BaseLlmClient (generate, generate_structured).
"""

import json
from typing import Any

from openai import OpenAI

from llm.base import BaseLlmClient, Message


class OpenAIClient(BaseLlmClient):
    """OpenAI chat completions via the OpenAI Python SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        """Build OpenAI client. Uses OPENAI_API_KEY if api_key is None."""
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._default_model = default_model

    def generate(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call chat.completions.create and return the assistant message text."""
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
