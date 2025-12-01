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
        self.channel.queue_declare(queue='video_processing_queue', durable=True)
        print("Connected to RabbitMQ")

    def publish_event(self, message: dict):
        """
        Publishes a message.
        """
        self._ensure_connection()
        self.channel.basic_publish(
            exchange='',
            routing_key='video_processing_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def _ensure_connection(self):
        if self.connection is None or self.connection.is_closed:
            self._connect()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()