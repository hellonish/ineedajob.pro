"""Google Gemini generate-content client.

Uses the google-genai SDK (client.models.generate_content) for completions.
Depends on GEMINI_API_KEY or GOOGLE_API_KEY. Implements BaseLlmClient (generate, generate_structured).
"""

import json
import re
from typing import Any

from google import genai
from google.genai import types

from llm.base import BaseLlmClient, Message


DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


class GeminiClient(BaseLlmClient):
    """Gemini completions via the Google GenAI SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = DEFAULT_GEMINI_MODEL,
    ) -> None:
        """Build Gemini client. Uses GEMINI_API_KEY or GOOGLE_API_KEY if api_key is None."""
        self._client = genai.Client(api_key=api_key)
        self._default_model = default_model

    def generate(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call generate_content with converted contents and return response text."""
        model = model or self._default_model
        system_instruction, contents = self._to_gemini_contents(messages)
        config_kwargs: dict[str, Any] = {}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        for key in ("temperature", "max_output_tokens", "top_p", "top_k"):
            if key in kwargs:
                config_kwargs[key] = kwargs.pop(key)
        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
        response = self._client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
            **kwargs,
        )
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
        return self._parse_json_from_response(raw or "")

    def _parse_json_from_response(self, raw: str) -> dict[str, Any]:
        """Strip markdown code fences if present and parse JSON; return {} on failure."""
        text = (raw or "").strip()
        if not text:
            return {}
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    def _to_gemini_contents(self, messages: list[Message]) -> tuple[str | None, Any]:
        """Convert base messages to system_instruction (or None) and contents for Gemini."""
        system_parts: list[str] = []
        contents: list[types.Content] = []
        for m in messages:
            role = m.get("role", "user")
            content = (m.get("content") or "").strip()
            if role == "system":
                system_parts.append(content)
                continue
            if role == "user":
                contents.append(types.Content(role="user", parts=[types.Part(text=content)]))
            elif role == "assistant":
                contents.append(
                    types.Content(role="model", parts=[types.Part(text=content)])
                )
        system = "\n".join(system_parts) if system_parts else None
        if not contents:
            contents = [types.Content(role="user", parts=[types.Part(text="")])]
        return system, contents

    def _extract_text(self, response: Any) -> str:
        """Get text from GenerateContentResponse."""
        if not response or not response.candidates:
            return ""
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            return ""
        return (candidate.content.parts[0].text or "").strip()
