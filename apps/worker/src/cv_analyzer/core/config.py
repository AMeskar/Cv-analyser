"""Worker configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Worker settings."""
    
    # Worker
    worker_name: str = "cv-analyzer-worker"
    poll_interval: int = 5  # seconds
    
    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "cv-analyzer"
    minio_secure: bool = False
    
    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_queue_name: str = "cv_analysis_queue"
    
    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "cvanalyzer"
    postgres_password: str = "cvanalyzer"
    postgres_db: str = "cvanalyzer"
    
    # AI Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_provider: str = "openai"
    
    # MLflow
    mlflow_tracking_uri: str = "http://mlflow:5000"
    mlflow_experiment_name: str = "cv-analysis"
    
    # n8n
    n8n_webhook_url: Optional[str] = None
    
    # Observability
    otel_exporter_otlp_endpoint: Optional[str] = None
    service_name: str = "cv-analyzer-worker"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
