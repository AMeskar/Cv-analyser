"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API
    api_title: str = "CV Analyzer API"
    api_version: str = "v1"
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    
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
    
    # File upload
    max_file_size_mb: int = 10
    allowed_file_types: list[str] = [".pdf", ".docx", ".txt"]
    
    # AI Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_provider: str = "openai"
    
    # n8n
    n8n_webhook_url: Optional[str] = None
    
    # MLflow
    mlflow_tracking_uri: str = "http://mlflow:5000"
    
    # Observability
    otel_exporter_otlp_endpoint: Optional[str] = None
    service_name: str = "cv-analyzer-backend"
    
    # Auth (OIDC stub)
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
