"""Anthropic Claude messages client.

Uses the Anthropic SDK (messages.create) for completions. Depends on
ANTHROPIC_API_KEY. Implements BaseLlmClient (generate, generate_structured).
"""

import json
from typing import Any

from anthropic import Anthropic

from llm.base import BaseLlmClient, Message


DEFAULT_MAX_TOKENS = 1024
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


class AnthropicClient(BaseLlmClient):
    """Anthropic Claude completions via the Messages API."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = DEFAULT_ANTHROPIC_MODEL,
        default_max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> None:
        """Build Anthropic client. Uses ANTHROPIC_API_KEY if api_key is None."""
        self._client = Anthropic(api_key=api_key)
        self._default_model = default_model
        self._default_max_tokens = default_max_tokens

    def generate(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call messages.create and return the first assistant text block."""
        model = model or self._default_model
        max_tokens = kwargs.pop("max_tokens", self._default_max_tokens)
        anthropic_messages, system = self._to_anthropic_messages_and_system(messages)
        create_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": anthropic_messages,
            **kwargs,
        }
        if system:
            create_kwargs["system"] = system
        response = self._client.messages.create(**create_kwargs)
        return self._extract_text(response)

    def generate_structured(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate with JSON-only instruction appended; return parsed dict."""
        structured_suffix: list[Message] = [
            {"role": "user", "content": "Respond with a single valid JSON object only, no other text."},
        ]
        combined = messages + structured_suffix
        raw = self.generate(combined, model=model, **kwargs)
        return json.loads(raw) if raw else {}

    def _to_anthropic_messages_and_system(
        self, messages: list[Message]
    ) -> tuple[list[dict[str, Any]], str]:
        """Split into messages (user/assistant only) and system string."""
        out: list[dict[str, Any]] = []
        system_parts: list[str] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "") or ""
            if role == "system":
                system_parts.append(content)
                continue
            if role in ("user", "assistant"):
                out.append({"role": role, "content": content})
        system = "\n".join(system_parts) if system_parts else ""
        return out, system

    def _extract_text(self, response: Any) -> str:
        """Get the first text block from the last content block."""
        if not response.content:
            return ""
        for block in response.content:
            if getattr(block, "type", None) == "text":
                return getattr(block, "text", "") or ""
        return ""
