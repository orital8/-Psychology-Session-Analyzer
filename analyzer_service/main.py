import json
import logging
import sys
from minio_utils import MinioClient
from rabbitmq_utils import RabbitMQClient
from mongo_utils import MongoClientWrapper
from llm_client import LLMAnalyzer

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analyzer_service")

def process_analysis(ch, method, properties, body):
    try:
        message = json.loads(body)
        logger.info(f"Received task: {message}")
        
    
        video_id = message.get('video_id')
        user_id = message.get('user_id', 'anonymous') 
        transcript_filename = message.get('transcript_filename')
        
        minio = MinioClient()
        rabbitmq = RabbitMQClient()
        mongo = MongoClientWrapper()
        llm = LLMAnalyzer()

        # 1. Get Transcript
        logger.info(f"Fetching transcript: {transcript_filename}...")
        transcript_data = minio.download_json(transcript_filename)

        # 2. Analyze
        logger.info("Running Psychological Analysis...")
        analysis_result = llm.analyze_transcript(transcript_data)

        # 3. Save to MinIO (File Storage)
        analysis_filename = f"{video_id}-analysis.json"
        logger.info(f"Saving file to MinIO: {analysis_filename}...")
        minio.upload_json(analysis_result, analysis_filename)

        # 4. Save to MongoDB (Query Storage)
        logger.info(f"Saving record to MongoDB for User: {user_id}...")
        mongo.save_analysis(user_id, video_id, analysis_result)

        # 5. Publish Completion
        next_event = {
            "user_id": user_id,
            "video_id": video_id,
            "analysis_file": analysis_filename,
            "status": "analysis_completed"
        }
        rabbitmq.publish_event(next_event)
        logger.info("Analysis complete. Event published.")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    rabbitmq = RabbitMQClient()
    rabbitmq.consume(process_analysis)