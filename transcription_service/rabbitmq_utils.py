import pika
import json
from config import settings

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None

    def _connect(self):
        
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declare queues
        self.channel.queue_declare(queue='audio_processing_queue', durable=True)
        self.channel.queue_declare(queue='transcription_processing_queue', durable=True)
        
        print("Connected to RabbitMQ")

    def publish_event(self, message: dict, queue_name='transcription_processing_queue'):
        self._ensure_connection()
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def consume(self, callback_function):
        self._ensure_connection()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='audio_processing_queue', 
            on_message_callback=callback_function
        )
        print("Waiting for messages...")
        self.channel.start_consuming()

    def _ensure_connection(self):
        if self.connection is None or self.connection.is_closed:
            self._connect()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()