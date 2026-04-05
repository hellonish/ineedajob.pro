"""Base LLM client interface.

Defines the abstract contract for LLM providers. All provider-specific clients
(OpenAIClient, AnthropicClient, GeminiClient, DeepSeekClient) implement
generate() and generate_structured() so callers can swap providers without changing code.
"""

from abc import ABC, abstractmethod
from typing import Any


Message = dict[str, str]
"""Single chat message: {"role": "user"|"assistant"|"system", "content": "..."}."""


class BaseLlmClient(ABC):
    """Abstract LLM client. Subclasses implement generate() and generate_structured()."""

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a single non-streaming completion.

        Args:
            messages: Chat history; each item has "role" and "content".
            model: Model name; uses client default if None.
            **kwargs: Provider-specific options (e.g. max_tokens, temperature).

        Returns:
            Generated text from the assistant.
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a completion constrained to valid JSON; returns parsed dict.

        Args:
            messages: Chat history; each item has "role" and "content".
            model: Model name; uses client default if None.
            **kwargs: Provider-specific options (e.g. max_tokens, temperature).

        Returns:
            Parsed JSON object from the assistant response.
        """
        pass
