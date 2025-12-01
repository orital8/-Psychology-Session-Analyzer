from minio import Minio
from config import settings
import os

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False
        )
        self.bucket = settings.MINIO_BUCKET_NAME

    def download_file(self, object_name, file_path):
        """Downloads file from MinIO to local path"""
        self.client.fget_object(self.bucket, object_name, file_path)

    def upload_file(self, file_path, object_name, content_type):
        """Uploads local file to MinIO"""
        self.client.fput_object(
            self.bucket,
            object_name,
            file_path,
            content_type=content_type
        )