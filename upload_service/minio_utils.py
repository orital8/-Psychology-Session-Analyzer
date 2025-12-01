from minio import Minio
import io
from config import settings

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(self, file_data: bytes, filename: str, content_type: str):
        file_stream = io.BytesIO(file_data)
        self.client.put_object(
            self.bucket,
            filename,
            file_stream,
            length=len(file_data),
            content_type=content_type
        )
        return filename