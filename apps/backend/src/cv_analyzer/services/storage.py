"""MinIO storage service."""
import io
from typing import Optional
from minio import Minio
from minio.error import S3Error
from cv_analyzer.core.config import settings
from cv_analyzer.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Service for file storage in MinIO."""
    
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure bucket exists."""
        try:
            if not self.client.bucket_exists(settings.minio_bucket):
                self.client.make_bucket(settings.minio_bucket)
                logger.info("created_bucket", bucket=settings.minio_bucket)
        except S3Error as e:
            logger.error("bucket_creation_failed", error=str(e))
            raise
    
    def upload_file(self, file_id: str, file_data: bytes, content_type: str) -> str:
        """
        Upload file to MinIO.
        
        Args:
            file_id: Unique file identifier
            file_data: File content as bytes
            content_type: MIME type
            
        Returns:
            Object path/key
        """
        object_name = f"cvs/{file_id}"
        try:
            self.client.put_object(
                settings.minio_bucket,
                object_name,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            logger.info("file_uploaded", file_id=file_id, object_name=object_name)
            return object_name
        except S3Error as e:
            logger.error("file_upload_failed", file_id=file_id, error=str(e))
            raise
    
    def download_file(self, file_id: str) -> bytes:
        """
        Download file from MinIO.
        
        Args:
            file_id: File identifier
            
        Returns:
            File content as bytes
        """
        object_name = f"cvs/{file_id}"
        try:
            response = self.client.get_object(settings.minio_bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info("file_downloaded", file_id=file_id, object_name=object_name)
            return data
        except S3Error as e:
            logger.error("file_download_failed", file_id=file_id, error=str(e))
            raise
    
    def delete_file(self, file_id: str):
        """
        Delete file from MinIO.
        
        Args:
            file_id: File identifier
        """
        object_name = f"cvs/{file_id}"
        try:
            self.client.remove_object(settings.minio_bucket, object_name)
            logger.info("file_deleted", file_id=file_id, object_name=object_name)
        except S3Error as e:
            logger.error("file_delete_failed", file_id=file_id, error=str(e))
            raise
    
    def get_presigned_url(self, file_id: str, expires_seconds: int = 3600) -> str:
        """
        Get presigned URL for file access.
        
        Args:
            file_id: File identifier
            expires_seconds: URL expiration time
            
        Returns:
            Presigned URL
        """
        object_name = f"cvs/{file_id}"
        try:
            url = self.client.presigned_get_object(
                settings.minio_bucket,
                object_name,
                expires=expires_seconds,
            )
            return url
        except S3Error as e:
            logger.error("presigned_url_failed", file_id=file_id, error=str(e))
            raise


storage_service = StorageService()
