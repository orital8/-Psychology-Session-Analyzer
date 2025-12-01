import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DataDog / General
    SERVICE_NAME: str = "upload-service"
    
    # RabbitMQ Settings
    RABBITMQ_HOST: str = "rabbitmq_broker" # Matches docker service name
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    # MinIO Settings
    MINIO_ENDPOINT: str = "minio_storage:9000" # Matches docker service name
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str = "therapy-videos"

    class Config:
        env_file = ".env" # It will look for .env in the root when running via Docker
        extra = "ignore"

settings = Settings()