from minio import Minio
from config import settings
import json

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False
        )
        self.analysis_bucket = settings.MINIO_ANALYSIS_BUCKET

    def list_analyses(self):
        if not self.client.bucket_exists(self.analysis_bucket):
            return []
        objects = self.client.list_objects(self.analysis_bucket)
        return [obj.object_name for obj in objects]

    def get_analysis(self, object_name):
        try:
            response = self.client.get_object(self.analysis_bucket, object_name)
            return json.load(response)
        finally:
            if 'response' in locals():
                response.close()