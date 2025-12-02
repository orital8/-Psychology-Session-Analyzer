import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "analyzer-service"
    
    # LLM Settings
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-5-nano-2025-08-07" 
    
    # Infrastructure
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    MONGO_URI: str = "mongodb://mongo:27017" # Default inside Docker
    
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASS: str

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str = "therapy-videos"
    MINIO_ANALYSIS_BUCKET: str = "therapy-analysis"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()