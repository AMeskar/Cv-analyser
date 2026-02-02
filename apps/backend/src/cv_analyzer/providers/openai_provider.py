"""OpenAI provider implementation."""
import time
from typing import Optional
from openai import OpenAI
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger
from cv_analyzer.providers.base import AIProvider, ProviderResponse

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"
    
    async def analyze_cv(
        self,
        cv_text: str,
        prompt_template: str,
        prompt_version: str,
    ) -> ProviderResponse:
        """Analyze CV using OpenAI."""
        start_time = time.time()
        
        try:
            # Format prompt
            full_prompt = prompt_template.format(cv_text=cv_text)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert CV analyzer."},
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            logger.info(
                "openai_analysis_complete",
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
                    "finish_reason": response.choices[0].finish_reason,
                },
            )
        except Exception as e:
            logger.error("openai_analysis_failed", error=str(e))
            raise
    
    def get_provider_name(self) -> str:
        return "openai"
