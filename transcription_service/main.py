import os
import json
import sys
import time
import requests
import logging
from minio_utils import MinioClient
from rabbitmq_utils import RabbitMQClient
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("transcription_service")

# AssemblyAI Constants
UPLOAD_URL = 'https://api.assemblyai.com/v2/upload'
TRANSCRIPT_URL = 'https://api.assemblyai.com/v2/transcript'
HEADERS = {"authorization": settings.ASSEMBLYAI_API_KEY}

def upload_file_to_api(file_path):
    """Streams file to AssemblyAI"""
    logger.info("Uploading audio to AssemblyAI...")
    def read_file(path):
        with open(path, 'rb') as f:
            while True:
                data = f.read(3145728) # Read in 3MB chunks
                if not data: break
                yield data

    response = requests.post(UPLOAD_URL, headers=HEADERS, data=read_file(file_path))
    response.raise_for_status() # Crash if API rejects us
    return response.json()['upload_url']

def start_transcription(audio_url):
    """Starts job with Speaker Diarization enabled"""
    logger.info("Starting transcription with Speaker Diarization...")
    json_payload = {
        "audio_url": audio_url,
        "speaker_labels": True 
    }
    response = requests.post(TRANSCRIPT_URL, json=json_payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()['id']

def wait_for_completion(transcript_id):
    """Polls API until done"""
    polling_endpoint = f"{TRANSCRIPT_URL}/{transcript_id}"
    
    while True:
        response = requests.get(polling_endpoint, headers=HEADERS)
        response.raise_for_status()
        status = response.json()['status']
        
        if status == 'completed':
            return response.json()
        elif status == 'error':
            raise Exception(f"Transcription failed: {response.json()['error']}")
            
        logger.info(f"Transcription status: {status}...")
        time.sleep(3)

def process_audio(ch, method, properties, body):
    try:
        message = json.loads(body)
        logger.info(f"Received message: {message}")
        
        video_id = message['video_id']
        audio_filename = message['audio_filename']
        
        local_audio_path = f"/tmp/{audio_filename}"
        local_json_path = f"/tmp/{video_id}.json"
        
        minio = MinioClient()
        rabbitmq = RabbitMQClient()

        # 1. Download
        logger.info(f"Downloading {audio_filename}...")
        minio.download_file(audio_filename, local_audio_path)

        # 2. Transcribe via AssemblyAI
        upload_url = upload_file_to_api(local_audio_path)
        transcript_id = start_transcription(upload_url)
        result_json = wait_for_completion(transcript_id)

        # 3. Save Result locally
        with open(local_json_path, 'w') as f:
            json.dump(result_json, f)

        # 4. Upload JSON to MinIO
        logger.info("Uploading JSON transcript...")
        json_filename = f"{video_id}.json"
        minio.upload_file(local_json_path, json_filename, "application/json")

        # 5. Publish Event
        next_event = {
            "video_id": video_id,
            "transcript_filename": json_filename,
            "status": "transcribed"
        }
        rabbitmq.publish_event(next_event)
        logger.info("Event published to transcription_processing_queue")

        # 6. Cleanup
        if os.path.exists(local_audio_path): os.remove(local_audio_path)
        if os.path.exists(local_json_path): os.remove(local_json_path)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Failed to process audio: {e}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    rabbitmq = RabbitMQClient()
    rabbitmq.consume(process_audio)