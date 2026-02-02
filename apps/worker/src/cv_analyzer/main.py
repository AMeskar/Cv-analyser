"""Worker main entry point."""
import asyncio
import json
import time
from datetime import datetime
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import start_http_server

from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import configure_logging, get_logger
from cv_analyzer.core.metrics import (
    jobs_processed_total,
    job_processing_duration_seconds,
)
from cv_analyzer.services.storage import StorageService
from cv_analyzer.services.queue import QueueService
from cv_analyzer.services.job_tracker import JobTracker
from cv_analyzer.services.mlflow_client import MLflowClient

storage_service = StorageService()
queue_service = QueueService()
job_tracker = JobTracker()
mlflow_client = MLflowClient()
from cv_analyzer.analyzers.analyzer import CVAnalyzer

# Configure logging
configure_logging(settings.service_name, False)
logger = get_logger(__name__)

# Configure OpenTelemetry
if settings.otel_exporter_otlp_endpoint:
    trace.set_tracer_provider(TracerProvider())
    otlp_exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

# Start Prometheus metrics server
start_http_server(9090)


async def process_job(job_data: dict):
    """Process a single CV analysis job."""
    job_id = job_data["job_id"]
    cv_id = job_data["cv_id"]
    provider_name = job_data["provider"]
    prompt_version = job_data.get("prompt_version", "v1")
    
    with tracer.start_as_current_span("process_job") as span:
        span.set_attribute("job_id", job_id)
        span.set_attribute("cv_id", cv_id)
        span.set_attribute("provider", provider_name)
        
        start_time = time.time()
        
        try:
            # Update job status
            job_tracker.update_job_status(job_id, "processing")
            job_tracker.add_timeline_event(job_id, "processing_started", "Started processing CV")
            
            # Download CV from MinIO
            logger.info("downloading_cv", cv_id=cv_id)
            cv_data = storage_service.download_file(cv_id)
            job_tracker.add_timeline_event(job_id, "cv_downloaded", "Downloaded CV from storage")
            
            # Analyze CV
            analyzer = CVAnalyzer()
            result = await analyzer.analyze(
                cv_data=cv_data,
                filename=f"{cv_id}.pdf",  # TODO: Store filename in metadata
                provider_name=provider_name,
                prompt_version=prompt_version,
            )
            
            job_tracker.add_timeline_event(
                job_id,
                "analysis_complete",
                "AI analysis completed",
                {"provider": provider_name, "tokens": result["provider"]["tokens_used"]},
            )
            
            # Log to MLflow
            logger.info("logging_to_mlflow", job_id=job_id)
            mlflow_client.log_run(
                job_id=job_id,
                cv_id=cv_id,
                provider=provider_name,
                prompt_version=prompt_version,
                result=result,
            )
            job_tracker.add_timeline_event(job_id, "mlflow_logged", "Logged experiment to MLflow")
            
            # Store report (TODO: Store in database/storage)
            # For now, we'll just mark as complete
            
            # Trigger n8n webhook (if configured)
            if settings.n8n_webhook_url:
                # TODO: Call n8n webhook
                pass
            
            # Update job status
            job_tracker.update_job_status(job_id, "completed")
            job_tracker.add_timeline_event(job_id, "job_completed", "Job completed successfully")
            
            duration = time.time() - start_time
            jobs_processed_total.labels(status="success", provider=provider_name).inc()
            job_processing_duration_seconds.labels(provider=provider_name).observe(duration)
            
            logger.info("job_completed", job_id=job_id, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            logger.error("job_failed", job_id=job_id, error=error_msg, duration=duration)
            
            job_tracker.update_job_status(job_id, "failed", error=error_msg)
            job_tracker.add_timeline_event(job_id, "job_failed", f"Job failed: {error_msg}")
            
            jobs_processed_total.labels(status="failed", provider=provider_name).inc()
            job_processing_duration_seconds.labels(provider=provider_name).observe(duration)
            
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_msg))


async def worker_loop():
    """Main worker loop."""
    logger.info("worker_starting", service=settings.service_name)
    
    while True:
        try:
            # Dequeue job
            job_data = queue_service.dequeue_job(timeout=settings.poll_interval)
            
            if job_data:
                await process_job(job_data)
            else:
                # No job available, continue polling
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("worker_stopping")
            break
        except Exception as e:
            logger.error("worker_error", error=str(e))
            await asyncio.sleep(5)  # Back off on error


if __name__ == "__main__":
    asyncio.run(worker_loop())
