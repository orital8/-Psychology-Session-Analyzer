import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "query-service"
    
    # LLM & DB
    OPENAI_API_KEY: str
    MONGO_URI: str = "mongodb://mongo:27017"
    LLM_MODEL: str = "gpt-5-nano-2025-08-07"
    
    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str = "therapy-videos"
    MINIO_ANALYSIS_BUCKET: str = "therapy-analysis"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()