"""Prompt templates for CV analysis."""
from typing import Dict
from cv_analyzer.core.logging import get_logger

logger = get_logger(__name__)

PROMPTS: Dict[str, str] = {
    "v1": """Analyze the following CV and provide a comprehensive assessment.

CV Content:
{cv_text}

Please provide:
1. Overall score (0-100) with justification
2. Detected skills (list)
3. Identified gaps (list)
4. Seniority level assessment (junior/mid/senior/lead)
5. ATS (Applicant Tracking System) compatibility issues (list)
6. Improvement recommendations (structured plan)

Format your response as JSON with the following structure:
{{
    "overall_score": <number>,
    "score_breakdown": {{
        "content_quality": <number>,
        "structure": <number>,
        "skills_match": <number>,
        "ats_compatibility": <number>
    }},
    "skills": ["skill1", "skill2", ...],
    "gaps": ["gap1", "gap2", ...],
    "seniority_level": "<level>",
    "ats_issues": ["issue1", "issue2", ...],
    "improvement_plan": "<detailed recommendations>",
    "summary": "<overall assessment summary>"
}}
""",
    
    "v2": """You are an expert CV reviewer. Analyze this CV thoroughly.

CV:
{cv_text}

Provide a detailed analysis including:
- Quantitative scores (0-100) for key dimensions
- Skills extraction and categorization
- Career progression assessment
- ATS optimization feedback
- Actionable improvement recommendations

Return structured JSON matching this schema:
{{
    "overall_score": <0-100>,
    "scores": [
        {{"category": "Content Quality", "score": <0-100>, "description": "..."}},
        {{"category": "Structure", "score": <0-100>, "description": "..."}},
        {{"category": "Skills Presentation", "score": <0-100>, "description": "..."}},
        {{"category": "ATS Compatibility", "score": <0-100>, "description": "..."}}
    ],
    "skills": ["skill1", "skill2"],
    "gaps": ["gap1", "gap2"],
    "seniority_level": "<level>",
    "ats_issues": ["issue1"],
    "improvement_plan": "<detailed plan>",
    "summary": "<summary>"
}}
""",
}


def get_prompt(version: str = "v1") -> str:
    """Get prompt template by version."""
    if version not in PROMPTS:
        logger.warning("prompt_version_not_found", version=version, default="v1")
        version = "v1"
    return PROMPTS[version]
