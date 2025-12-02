import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "transcription-service"
    
    # AssemblyAI API Key (Reads from .env)
    ASSEMBLYAI_API_KEY: str

    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str = "therapy-videos"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()