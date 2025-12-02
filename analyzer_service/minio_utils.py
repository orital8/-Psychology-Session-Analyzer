from minio import Minio
from config import settings
import json
import io

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        self.analysis_bucket = settings.MINIO_ANALYSIS_BUCKET
        self._ensure_buckets()

    def _ensure_buckets(self):
        # Create buckets if they don't exist
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        if not self.client.bucket_exists(self.analysis_bucket):
            self.client.make_bucket(self.analysis_bucket)

    def download_json(self, object_name):
        response = self.client.get_object(self.bucket, object_name)
        return json.load(response)

    def upload_json(self, data, object_name):
        # Convert dict to bytes
        json_bytes = json.dumps(data, indent=2).encode('utf-8')
        json_stream = io.BytesIO(json_bytes)
        
        self.client.put_object(
            self.analysis_bucket,
            object_name,
            json_stream,
            length=len(json_bytes),
            content_type="application/json"
        )