"""Pydantic schemas for API requests/responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CVUploadResponse(BaseModel):
    """Response for CV upload."""
    cv_id: str = Field(..., description="Unique CV identifier")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")


class AnalyzeRequest(BaseModel):
    """Request to analyze a CV."""
    provider: Optional[str] = Field(None, description="AI provider to use (default: configured default)")
    prompt_version: Optional[str] = Field(None, description="Prompt template version")


class AnalyzeResponse(BaseModel):
    """Response for analysis trigger."""
    job_id: str = Field(..., description="Unique job identifier")
    cv_id: str = Field(..., description="CV identifier")
    status: JobStatus = Field(..., description="Initial job status")
    created_at: datetime = Field(..., description="Job creation timestamp")


class TimelineEvent(BaseModel):
    """Timeline event."""
    timestamp: datetime = Field(..., description="Event timestamp")
    event: str = Field(..., description="Event name")
    message: str = Field(..., description="Event message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class JobStatusResponse(BaseModel):
    """Response for job status."""
    job_id: str = Field(..., description="Job identifier")
    cv_id: str = Field(..., description="CV identifier")
    status: JobStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Job timeline")
    error: Optional[str] = Field(None, description="Error message if failed")


class Score(BaseModel):
    """Analysis score."""
    category: str = Field(..., description="Score category")
    score: float = Field(..., ge=0.0, le=100.0, description="Score value (0-100)")
    description: str = Field(..., description="Score description")


class AnalysisReport(BaseModel):
    """CV analysis report."""
    cv_id: str = Field(..., description="CV identifier")
    job_id: str = Field(..., description="Job identifier")
    provider: str = Field(..., description="AI provider used")
    prompt_version: str = Field(..., description="Prompt template version")
    scores: List[Score] = Field(..., description="Analysis scores")
    summary: str = Field(..., description="Analysis summary")
    skills: List[str] = Field(default_factory=list, description="Detected skills")
    gaps: List[str] = Field(default_factory=list, description="Identified gaps")
    seniority_level: Optional[str] = Field(None, description="Detected seniority level")
    ats_issues: List[str] = Field(default_factory=list, description="ATS compatibility issues")
    improvement_plan: str = Field(..., description="Improvement recommendations")
    raw_analysis: Dict[str, Any] = Field(..., description="Raw analysis JSON")
    generated_at: datetime = Field(..., description="Report generation timestamp")
