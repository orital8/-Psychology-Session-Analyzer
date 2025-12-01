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
        
        # Paths
        local_video_path = f"/tmp/{video_filename}"
        local_audio_path = f"/tmp/{video_id}.mp3"
        
        minio = MinioClient()
        rabbitmq = RabbitMQClient()

        # 2. Logic (No nested try/catch needed)
        logger.info(f"Downloading {video_filename}...")
        minio.download_file(video_filename, local_video_path)

        logger.info("Extracting audio...")
        video = VideoFileClip(local_video_path)
        video.audio.write_audiofile(local_audio_path, logger=None)
        video.close()

        logger.info("Uploading MP3...")
        mp3_filename = f"{video_id}.mp3"
        minio.upload_file(local_audio_path, mp3_filename, "audio/mpeg")

        # 3. Publish Next Event
        next_event = {
            "video_id": video_id,
            "audio_filename": mp3_filename,
            "status": "audio_extracted"
        }
        rabbitmq.publish_event(next_event)
        logger.info("Event published to audio_processing_queue")

        # 4. Cleanup & Acknowledge
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
        if os.path.exists(local_audio_path):
            os.remove(local_audio_path)
            
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # CRITICAL: 'exc_info=True' prints the full stack trace to Datadog.
        # This lets you see EXACTLY where the bug is.
        logger.error(f"Failed to process video {method.delivery_tag}: {e}", exc_info=True)
        
        # Nack the message so it isn't lost (dead letter or discard based on args)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    try:
        rabbitmq = RabbitMQClient()
        rabbitmq.consume(process_video)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)