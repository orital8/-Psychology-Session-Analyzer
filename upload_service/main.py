import logging
import uuid
import time
from fastapi import FastAPI, UploadFile, HTTPException
from contextlib import asynccontextmanager
from minio_utils import MinioClient
from rabbitmq_utils import RabbitMQClient

# Configure Logging (INFO level shows startup, ERROR shows crashes)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("upload_service")

# Global clients
minio_client = None
rabbitmq_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global minio_client, rabbitmq_client
    
    logger.info("Waiting for infrastructure to be ready...")
    time.sleep(5) 
    
    # We allow this to crash if infra is missing. 
    # Docker will restart the service until it works.
    minio_client = MinioClient()
    rabbitmq_client = RabbitMQClient()
    
    logger.info("Infrastructure connected successfully.")
    yield
    
    # Cleanup
    if rabbitmq_client:
        rabbitmq_client.close()

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_video(file: UploadFile):
    # Validation is fine, keep specific logic
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # NO TRY/EXCEPT HERE. 
    # If MinIO or RabbitMQ fails, Python will raise the exception,
    # FastAPI will log the stack trace to Datadog, and return 500 to the user.
    
    session_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1]
    new_filename = f"{session_id}.{file_ext}"

    logger.info(f"Starting process for {session_id} ({file.filename})")

    # Read content
    content = await file.read()
    
    # Upload to MinIO
    minio_client.upload_file(content, new_filename, file.content_type)
    
    # Publish Event
    event = {
        "video_id": session_id,
        "filename": new_filename,
        "original_name": file.filename,
        "status": "uploaded"
    }
    rabbitmq_client.publish_event(event)
    
    logger.info(f"Successfully uploaded and queued: {session_id}")

    return {
        "message": "Upload successful", 
        "video_id": session_id,
        "status": "processing_started"
    }