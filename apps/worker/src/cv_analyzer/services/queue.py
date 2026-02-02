"""Redis queue service."""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import redis
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger
from cv_analyzer.core.metrics import (
    queue_enqueued_total,
    queue_dequeued_total,
    queue_size,
)

logger = get_logger(__name__)


class QueueService:
    """Service for job queue management."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )
        self.queue_name = settings.redis_queue_name
    
    def enqueue_job(
        self,
        cv_id: str,
        provider: Optional[str] = None,
        prompt_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Enqueue a CV analysis job.
        
        Args:
            cv_id: CV identifier
            provider: AI provider to use
            prompt_version: Prompt template version
            metadata: Additional metadata
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "cv_id": cv_id,
            "provider": provider or settings.default_provider,
            "prompt_version": prompt_version,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        try:
            self.redis_client.lpush(
                self.queue_name,
                json.dumps(job_data),
            )
            queue_enqueued_total.labels(queue_name=self.queue_name).inc()
            self._update_queue_size()
            logger.info("job_enqueued", job_id=job_id, cv_id=cv_id)
            return job_id
        except Exception as e:
            logger.error("job_enqueue_failed", job_id=job_id, error=str(e))
            raise
    
    def dequeue_job(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Dequeue a job from the queue.
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            Job data or None
        """
        try:
            result = self.redis_client.brpop(self.queue_name, timeout=timeout)
            if result:
                _, job_json = result
                job_data = json.loads(job_json)
                queue_dequeued_total.labels(queue_name=self.queue_name).inc()
                self._update_queue_size()
                logger.info("job_dequeued", job_id=job_data.get("job_id"))
                return job_data
            return None
        except Exception as e:
            logger.error("job_dequeue_failed", error=str(e))
            raise
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self.redis_client.llen(self.queue_name)
    
    def _update_queue_size(self):
        """Update queue size metric."""
        size = self.get_queue_size()
        queue_size.labels(queue_name=self.queue_name).set(size)
