"""
LLM Client - Provider-agnostic base class for structured LLM outputs.

All engine modules receive an LLMClient via dependency injection.
The API layer creates the right instance based on user settings.

Supported providers: grok (xAI), gemini (Google), deepseek
"""

import os
from typing import Optional, Dict, List, Any, Type

import instructor
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """
    Provider-agnostic LLM client for structured outputs.

    Wraps instructor + OpenAI-compatible API. Any provider that exposes
    an OpenAI-compatible chat completions endpoint works out of the box.

    Usage::

        llm = LLMClient(provider="grok", model="grok-3")
        result = llm.complete(
            response_model=MyPydanticModel,
            messages=[
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
            ],
            temperature=0.7,
        )
        # result is an instance of MyPydanticModel
    """

    PROVIDERS: Dict[str, Dict[str, Any]] = {
        "grok": {
            "base_url": "https://api.x.ai/v1",
            "env_key": "XAI_API_KEY",
            "default_model": "grok-3",
            "models": ["grok-3", "grok-3-mini"],
        },
        "gemini": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "env_key": "GEMINI_API_KEY",
            "default_model": "gemini-2.5-pro",
            "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com",
            "env_key": "DEEPSEEK_API_KEY",
            "default_model": "deepseek-chat",
            "models": ["deepseek-chat", "deepseek-reasoner"],
        },
    }

    def __init__(
        self,
        provider: str = "grok",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Args:
            provider: One of "grok", "gemini", "deepseek".
            model:    Model name. Falls back to provider's default.
            api_key:  API key. Falls back to the provider's env var.

        Raises:
            ValueError: Unknown provider or missing API key.
        """
        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Supported: {list(self.PROVIDERS.keys())}"
            )

        cfg = self.PROVIDERS[provider]
        self.provider = provider
        self.model: str = model or cfg["default_model"]

        key = api_key or os.getenv(cfg["env_key"])
        if not key:
            raise ValueError(
                f"API key missing for '{provider}'. "
                f"Set env var {cfg['env_key']} or pass api_key."
            )

        self._client = instructor.from_openai(
            OpenAI(base_url=cfg["base_url"], api_key=key, timeout=60.0),
            mode=instructor.Mode.JSON,
        )

    def complete(
        self,
        response_model: Type[Any],
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        max_retries: int = 2,
    ) -> Any:
        """
        Structured completion — returns an instance of *response_model*.

        Args:
            response_model: Pydantic BaseModel subclass.
            messages:       Chat message list.
            temperature:    Sampling temperature.
            max_tokens:     Max response tokens.
            max_retries:    Retries on transient failure.
        """
        return self._client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )

    @classmethod
    def from_user_settings(cls, settings: Dict[str, Any]) -> "LLMClient":
        """Create an LLMClient from a user's saved preferences dict."""
        return cls(
            provider=settings.get("llm_provider", "grok"),
            model=settings.get("llm_model"),
        )

    @classmethod
    def available_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Provider metadata for the UI (no secrets)."""
        return {
            name: {
                "default_model": cfg["default_model"],
                "models": cfg["models"],
            }
            for name, cfg in cls.PROVIDERS.items()
        }


def get_gemini_client(api_key: Optional[str] = None):
    """DEPRECATED — prefer LLMClient(provider='gemini')."""
    return LLMClient(provider="gemini", api_key=api_key)._client


def get_deepseek_client(api_key: Optional[str] = None):
    """DEPRECATED — prefer LLMClient(provider='deepseek')."""
    return LLMClient(provider="deepseek", api_key=api_key)._client
