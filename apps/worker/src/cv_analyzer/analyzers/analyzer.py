"""CV analysis orchestrator."""
import json
from typing import Dict, Any
from cv_analyzer.parsers.cv_parser import CVParser
from cv_analyzer.parsers.prompts import get_prompt
from cv_analyzer.providers.factory import get_provider
from cv_analyzer.core.logging import get_logger

logger = get_logger(__name__)


class CVAnalyzer:
    """Main CV analysis orchestrator."""
    
    def __init__(self):
        self.parser = CVParser()
    
    async def analyze(
        self,
        cv_data: bytes,
        filename: str,
        provider_name: str,
        prompt_version: str = "v1",
    ) -> Dict[str, Any]:
        """
        Analyze CV.
        
        Args:
            cv_data: CV file content
            filename: Original filename
            provider_name: AI provider name
            prompt_version: Prompt template version
            
        Returns:
            Analysis results
        """
        # Parse CV
        logger.info("parsing_cv", filename=filename)
        parsed_cv = self.parser.parse(cv_data, filename)
        
        # Get prompt template
        prompt_template = get_prompt(prompt_version)
        
        # Get AI provider
        provider = get_provider(provider_name)
        
        # Analyze with AI
        logger.info("analyzing_with_ai", provider=provider_name, prompt_version=prompt_version)
        ai_response = await provider.analyze_cv(
            cv_text=parsed_cv["normalized_text"],
            prompt_template=prompt_template,
            prompt_version=prompt_version,
        )
        
        # Parse AI response (expect JSON)
        try:
            analysis_json = json.loads(ai_response.content)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from markdown code blocks
            content = ai_response.content
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                analysis_json = json.loads(content[start:end].strip())
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                analysis_json = json.loads(content[start:end].strip())
            else:
                # Last resort: wrap in a structure
                analysis_json = {
                    "summary": ai_response.content,
                    "overall_score": 50,
                    "scores": [],
                    "skills": [],
                    "gaps": [],
                    "ats_issues": [],
                    "improvement_plan": "See summary",
                }
        
        # Combine results
        result = {
            "cv_metadata": {
                "filename": filename,
                "sections": parsed_cv["sections"],
            },
            "analysis": analysis_json,
            "provider": {
                "name": provider.get_provider_name(),
                "model": ai_response.model,
                "tokens_used": ai_response.tokens_used,
                "latency_ms": ai_response.latency_ms,
            },
            "prompt_version": prompt_version,
        }
        
        logger.info("analysis_complete", provider=provider_name, tokens=ai_response.tokens_used)
        
        return result
