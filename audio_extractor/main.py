import os
import json
import sys
import logging
from moviepy import VideoFileClip
from minio_utils import MinioClient
from rabbitmq_utils import RabbitMQClient

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audio_extractor")

def process_video(ch, method, properties, body):
    try:
        # 1. Parse Message
        message = json.loads(body)
        logger.info(f"Received message: {message}")
        
        video_id = message['video_id']
        video_filename = message['filename']
        # FIX: Capture user_id, default to 'anonymous' if missing (backward compatibility)
        user_id = message.get('user_id', 'anonymous')
        
        # Define local paths
        local_video_path = f"/tmp/{video_filename}"
        local_audio_path = f"/tmp/{video_id}.mp3"
        
        minio = MinioClient()
        rabbitmq = RabbitMQClient()

        # 2. Download Video
        logger.info(f"Downloading {video_filename}...")
        minio.download_file(video_filename, local_video_path)

        # 3. Extract Audio
        logger.info("Extracting audio...")
        video = VideoFileClip(local_video_path)
        video.audio.write_audiofile(local_audio_path, logger=None)
        video.close() 

        # 4. Upload Audio
        logger.info("Uploading MP3...")
        mp3_filename = f"{video_id}.mp3"
        minio.upload_file(local_audio_path, mp3_filename, "audio/mpeg")

        # 5. Publish Next Event
        next_event = {
            "user_id": user_id, # FIX: Pass it forward
            "video_id": video_id,
            "audio_filename": mp3_filename,
            "status": "audio_extracted"
        }
        rabbitmq.publish_event(next_event)
        logger.info("Event published to audio_processing_queue")

        # 6. Cleanup & Acknowledge
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
        if os.path.exists(local_audio_path):
            os.remove(local_audio_path)
            
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Failed to process video: {e}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    rabbitmq = RabbitMQClient()
    rabbitmq.consume(process_video)