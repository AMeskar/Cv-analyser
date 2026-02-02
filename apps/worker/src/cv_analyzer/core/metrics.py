"""Prometheus metrics."""
from prometheus_client import Counter, Histogram, Gauge

# Job processing metrics
jobs_processed_total = Counter(
    "jobs_processed_total",
    "Total jobs processed",
    ["status", "provider"],
)

job_processing_duration_seconds = Histogram(
    "job_processing_duration_seconds",
    "Job processing duration",
    ["provider"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0],
)

# AI provider metrics
ai_requests_total = Counter(
    "ai_requests_total",
    "Total AI provider requests",
    ["provider", "status"],
)

ai_request_duration_seconds = Histogram(
    "ai_request_duration_seconds",
    "AI provider request duration",
    ["provider"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

ai_tokens_used = Counter(
    "ai_tokens_used_total",
    "Total AI tokens used",
    ["provider", "type"],  # type: input/output
)

# CV parsing metrics
cv_parses_total = Counter(
    "cv_parses_total",
    "Total CVs parsed",
    ["file_type", "status"],
)

cv_parse_duration_seconds = Histogram(
    "cv_parse_duration_seconds",
    "CV parsing duration",
    ["file_type"],
)
