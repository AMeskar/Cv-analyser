"""Prometheus metrics."""
from prometheus_client import Counter, Histogram, Gauge

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# CV upload metrics
cv_uploads_total = Counter(
    "cv_uploads_total",
    "Total CV uploads",
    ["status"],
)

cv_upload_size_bytes = Histogram(
    "cv_upload_size_bytes",
    "CV upload size in bytes",
    buckets=[1024, 10240, 102400, 1048576, 10485760],  # 1KB to 10MB
)

# Job metrics
jobs_created_total = Counter(
    "jobs_created_total",
    "Total jobs created",
    ["status"],
)

jobs_in_progress = Gauge(
    "jobs_in_progress",
    "Number of jobs currently in progress",
)

# Queue metrics
queue_size = Gauge(
    "queue_size",
    "Current queue size",
    ["queue_name"],
)

queue_enqueued_total = Counter(
    "queue_enqueued_total",
    "Total items enqueued",
    ["queue_name"],
)

queue_dequeued_total = Counter(
    "queue_dequeued_total",
    "Total items dequeued",
    ["queue_name"],
)
