"""Base AI provider interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ProviderResponse(BaseModel):
    """Provider response model."""
    content: str
    model: str
    tokens_used: int
    latency_ms: float
    metadata: Dict[str, Any] = {}


class AIProvider(ABC):
    """Base interface for AI providers."""
    
    @abstractmethod
    async def analyze_cv(
        self,
        cv_text: str,
        prompt_template: str,
        prompt_version: str,
    ) -> ProviderResponse:
        """
        Analyze CV using AI provider.
        
        Args:
            cv_text: Extracted CV text
            prompt_template: Prompt template
            prompt_version: Prompt version identifier
            
        Returns:
            Provider response with analysis
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name."""
        pass
