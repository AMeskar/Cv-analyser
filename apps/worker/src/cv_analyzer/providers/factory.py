"""Provider factory."""
from typing import Optional
from cv_analyzer.core.config import settings
from cv_analyzer.providers.base import AIProvider
from cv_analyzer.providers.openai_provider import OpenAIProvider
from cv_analyzer.providers.anthropic_provider import AnthropicProvider


def get_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get AI provider instance.
    
    Args:
        provider_name: Provider name (openai, anthropic) or None for default
        
    Returns:
        AI provider instance
    """
    provider_name = provider_name or settings.default_provider
    
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
