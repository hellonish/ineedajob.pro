__all__ = ["AnthropicClient", "DeepSeekClient", "GeminiClient", "OpenAIClient"]


def __getattr__(name: str):
    """Lazy-load clients so only the requested provider's dependencies are required."""
    if name == "AnthropicClient":
        from .anthropic_client import AnthropicClient
        return AnthropicClient
    if name == "DeepSeekClient":
        from .deepseek_client import DeepSeekClient
        return DeepSeekClient
    if name == "GeminiClient":
        from .gemini_client import GeminiClient
        return GeminiClient
    if name == "OpenAIClient":
        from .openai_client import OpenAIClient
        return OpenAIClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
