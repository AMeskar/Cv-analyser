"""Job status tracking service."""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import redis
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger

logger = get_logger(__name__)


class JobStatus(str):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TimelineEvent:
    """Timeline event."""
    def __init__(self, timestamp: datetime, event: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        self.timestamp = timestamp
        self.event = event
        self.message = message
        self.metadata = metadata or {}


class JobTracker:
    """Service for tracking job status and timeline."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )
        self.job_prefix = "job:"
        self.timeline_prefix = "timeline:"
    
    def create_job(
        self,
        job_id: str,
        cv_id: str,
        provider: str,
        prompt_version: Optional[str] = None,
    ):
        """Create a new job record."""
        job_data = {
            "job_id": job_id,
            "cv_id": cv_id,
            "status": JobStatus.PENDING,
            "provider": provider,
            "prompt_version": prompt_version,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.redis_client.setex(
            f"{self.job_prefix}{job_id}",
            86400 * 7,  # 7 days TTL
            json.dumps(job_data),
        )
        self.add_timeline_event(job_id, "job_created", "Job created", {})
        logger.info("job_created", job_id=job_id, cv_id=cv_id)
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        error: Optional[str] = None,
    ):
        """Update job status."""
        job_data = self.get_job(job_id)
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        job_data["status"] = status
        job_data["updated_at"] = datetime.utcnow().isoformat()
        if error:
            job_data["error"] = error
        
        self.redis_client.setex(
            f"{self.job_prefix}{job_id}",
            86400 * 7,
            json.dumps(job_data),
        )
        logger.info("job_status_updated", job_id=job_id, status=status)
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data."""
        data = self.redis_client.get(f"{self.job_prefix}{job_id}")
        if data:
            return json.loads(data)
        return None
    
    def add_timeline_event(
        self,
        job_id: str,
        event: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add timeline event."""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "message": message,
            "metadata": metadata or {},
        }
        self.redis_client.lpush(
            f"{self.timeline_prefix}{job_id}",
            json.dumps(event_data),
        )
        self.redis_client.expire(f"{self.timeline_prefix}{job_id}", 86400 * 7)
        logger.debug("timeline_event_added", job_id=job_id, event=event)
    
    def get_timeline(self, job_id: str) -> List[TimelineEvent]:
        """Get job timeline."""
        events_json = self.redis_client.lrange(f"{self.timeline_prefix}{job_id}", 0, -1)
        events = []
        for event_json in reversed(events_json):  # Reverse to get chronological order
            event_data = json.loads(event_json)
            events.append(
                TimelineEvent(
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    event=event_data["event"],
                    message=event_data["message"],
                    metadata=event_data.get("metadata"),
                )
            )
        return events
