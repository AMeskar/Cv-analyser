"""FastAPI application."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import configure_logging, get_logger
from cv_analyzer.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
)
from cv_analyzer.models.schemas import (
    CVUploadResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    JobStatusResponse,
    AnalysisReport,
    JobStatus,
)
from cv_analyzer.services.storage import storage_service
from cv_analyzer.services.queue import queue_service
from cv_analyzer.services.job_tracker import job_tracker
import uuid
from datetime import datetime

# Configure logging
configure_logging(settings.service_name, settings.debug)
logger = get_logger(__name__)

# OpenTelemetry tracer
tracer = trace.get_tracer(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("application_starting", service=settings.service_name)
    yield
    logger.info("application_shutting_down", service=settings.service_name)


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry instrumentation
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware for HTTP metrics."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)
    
    return response


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.service_name}


@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    # Check dependencies
    try:
        # Check Redis
        queue_service.redis_client.ping()
        # Check MinIO
        storage_service.client.bucket_exists(settings.minio_bucket)
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": "ready", "service": settings.service_name}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post(f"{settings.api_prefix}/cv/upload", response_model=CVUploadResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV file.
    
    Returns CV ID for subsequent operations.
    """
    with tracer.start_as_current_span("upload_cv") as span:
        span.set_attribute("filename", file.filename)
        
        # Validate file type
        file_ext = None
        if file.filename:
            file_ext = "." + file.filename.split(".")[-1].lower()
        
        if file_ext not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {settings.allowed_file_types}",
            )
        
        # Read file
        file_data = await file.read()
        file_size = len(file_data)
        
        # Validate file size
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.max_file_size_mb}MB",
            )
        
        # TODO: Virus scan hook (placeholder)
        # virus_scan_result = await virus_scan(file_data)
        
        # Generate CV ID
        cv_id = str(uuid.uuid4())
        
        # Upload to MinIO
        content_type = file.content_type or "application/octet-stream"
        storage_service.upload_file(cv_id, file_data, content_type)
        
        span.set_attribute("cv_id", cv_id)
        span.set_attribute("file_size", file_size)
        
        logger.info("cv_uploaded", cv_id=cv_id, filename=file.filename, size=file_size)
        
        return CVUploadResponse(
            cv_id=cv_id,
            filename=file.filename or "unknown",
            size_bytes=file_size,
            uploaded_at=datetime.utcnow(),
        )


@app.post(f"{settings.api_prefix}/cv/{{cv_id}}/analyze", response_model=AnalyzeResponse)
async def analyze_cv(cv_id: str, request: AnalyzeRequest):
    """
    Trigger CV analysis.
    
    Returns job ID for status tracking.
    """
    with tracer.start_as_current_span("analyze_cv") as span:
        span.set_attribute("cv_id", cv_id)
        
        # Verify CV exists (try to download)
        try:
            storage_service.download_file(cv_id)
        except Exception as e:
            logger.error("cv_not_found", cv_id=cv_id, error=str(e))
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Enqueue job
        job_id = queue_service.enqueue_job(
            cv_id=cv_id,
            provider=request.provider,
            prompt_version=request.prompt_version,
        )
        
        # Create job tracker record
        job_tracker.create_job(
            job_id=job_id,
            cv_id=cv_id,
            provider=request.provider or settings.default_provider,
            prompt_version=request.prompt_version,
        )
        
        # Trigger n8n webhook (if configured)
        if settings.n8n_webhook_url:
            # TODO: Async webhook call
            pass
        
        span.set_attribute("job_id", job_id)
        logger.info("analysis_triggered", cv_id=cv_id, job_id=job_id)
        
        return AnalyzeResponse(
            job_id=job_id,
            cv_id=cv_id,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow(),
        )


@app.get(f"{settings.api_prefix}/jobs/{{job_id}}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and timeline."""
    with tracer.start_as_current_span("get_job_status") as span:
        span.set_attribute("job_id", job_id)
        
        job_data = job_tracker.get_job(job_id)
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        timeline = job_tracker.get_timeline(job_id)
        
        return JobStatusResponse(
            job_id=job_data["job_id"],
            cv_id=job_data["cv_id"],
            status=JobStatus(job_data["status"]),
            created_at=datetime.fromisoformat(job_data["created_at"]),
            updated_at=datetime.fromisoformat(job_data["updated_at"]),
            timeline=timeline,
            error=job_data.get("error"),
        )


@app.get(f"{settings.api_prefix}/cv/{{cv_id}}/report", response_model=AnalysisReport)
async def get_report(cv_id: str):
    """Get final analysis report."""
    with tracer.start_as_current_span("get_report") as span:
        span.set_attribute("cv_id", cv_id)
        
        # TODO: Fetch report from database/storage
        # For now, return 404
        raise HTTPException(status_code=404, detail="Report not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "cv_analyzer.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
