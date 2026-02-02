# Adding a New AI Provider

This guide explains how to add a new AI provider to the CV Analyzer platform.

## Steps

### 1. Create Provider Implementation

Create a new file in `apps/backend/src/cv_analyzer/providers/` and `apps/worker/src/cv_analyzer/providers/`:

```python
# apps/backend/src/cv_analyzer/providers/new_provider.py
import time
from typing import Optional
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger
from cv_analyzer.providers.base import AIProvider, ProviderResponse

logger = get_logger(__name__)


class NewProvider(AIProvider):
    """New AI provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.new_provider_api_key
        if not self.api_key:
            raise ValueError("New Provider API key not configured")
        # Initialize client here
        self.model = "model-name"
    
    async def analyze_cv(
        self,
        cv_text: str,
        prompt_template: str,
        prompt_version: str,
    ) -> ProviderResponse:
        """Analyze CV using new provider."""
        start_time = time.time()
        
        try:
            # Format prompt
            full_prompt = prompt_template.format(cv_text=cv_text)
            
            # Call provider API
            # ... implementation ...
            
            latency_ms = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=response_content,
                model=self.model,
                tokens_used=tokens,
                latency_ms=latency_ms,
                metadata={
                    "prompt_version": prompt_version,
                    # ... other metadata ...
                },
            )
        except Exception as e:
            logger.error("provider_analysis_failed", error=str(e))
            raise
    
    def get_provider_name(self) -> str:
        return "new-provider"
```

### 2. Update Factory

Add provider to factory in `apps/backend/src/cv_analyzer/providers/factory.py` and `apps/worker/src/cv_analyzer/providers/factory.py`:

```python
from cv_analyzer.providers.new_provider import NewProvider

def get_provider(provider_name: Optional[str] = None) -> AIProvider:
    # ... existing code ...
    elif provider_name == "new-provider":
        return NewProvider()
    # ... rest of code ...
```

### 3. Update Configuration

Add API key configuration in `apps/backend/src/cv_analyzer/core/config.py` and `apps/worker/src/cv_analyzer/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    new_provider_api_key: Optional[str] = None
```

### 4. Update Kubernetes Secrets

Add secret key in `clusters/dev/infrastructure/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-provider-keys
  namespace: cv-analyzer
type: Opaque
stringData:
  # ... existing keys ...
  new-provider-api-key: "your-api-key-here"
```

### 5. Update Deployments

Add environment variable in `apps/backend/k8s/deployment.yaml` and `apps/worker/k8s/deployment.yaml`:

```yaml
env:
  # ... existing env vars ...
  - name: NEW_PROVIDER_API_KEY
    valueFrom:
      secretKeyRef:
        name: ai-provider-keys
        key: new-provider-api-key
```

### 6. Test

Test the new provider:

```python
from cv_analyzer.providers.factory import get_provider

provider = get_provider("new-provider")
response = await provider.analyze_cv(cv_text, prompt_template, "v1")
```

### 7. Update Documentation

Update `README.md` and `ARCHITECTURE.md` to mention the new provider.

## Best Practices

- Follow the existing provider pattern
- Add proper error handling
- Log all API calls (with redaction for sensitive data)
- Track metrics (tokens, latency, errors)
- Add unit tests
- Update prompt templates if needed
