"""Anthropic provider implementation."""
import time
from typing import Optional
from anthropic import Anthropic
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger
from cv_analyzer.providers.base import AIProvider, ProviderResponse

logger = get_logger(__name__)


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"
    
    async def analyze_cv(
        self,
        cv_text: str,
        prompt_template: str,
        prompt_version: str,
    ) -> ProviderResponse:
        """Analyze CV using Anthropic."""
        start_time = time.time()
        
        try:
            # Format prompt
            full_prompt = prompt_template.format(cv_text=cv_text)
            
            # Call Anthropic API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": full_prompt},
                ],
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            content = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            
            logger.info(
                "anthropic_analysis_complete",
                model=self.model,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
            )
            
            return ProviderResponse(
                content=content,
                model=self.model,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                metadata={
                    "prompt_version": prompt_version,
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
            )
        except Exception as e:
            logger.error("anthropic_analysis_failed", error=str(e))
            raise
    
    def get_provider_name(self) -> str:
        return "anthropic"
