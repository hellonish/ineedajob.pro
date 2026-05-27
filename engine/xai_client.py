"""Shared X.AI structured-output client used by engine modules."""

import os
from typing import Any, Dict, List, Optional, Type

import instructor
from dotenv import load_dotenv
from openai import OpenAI


XAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_XAI_MODEL = "grok-3"


class XAIStructuredClient:
    """Small X.AI client matching the engine's structured LLM interface."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize from explicit values or `.env`."""

        load_dotenv()
        key = api_key or os.getenv("XAI_API_KEY")
        if not key:
            raise ValueError("XAI_API_KEY is required in .env or the environment.")
        self.model = model or os.getenv("XAI_MODEL") or DEFAULT_XAI_MODEL
        self._client = instructor.from_openai(
            OpenAI(base_url=XAI_BASE_URL, api_key=key, timeout=120.0),
            mode=instructor.Mode.JSON,
        )

    def complete(
        self,
        response_model: Type[Any],
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 24000,
        max_retries: int = 2,
    ) -> Any:
        """Return a structured response model from X.AI."""

        return self._client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            strict=False,
        )
