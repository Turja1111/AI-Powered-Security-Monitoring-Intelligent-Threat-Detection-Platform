import json
import logging
from django.conf import settings
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class SecurityLogKafkaProducer:
    """Producer class to publish ingested log events to Apache Kafka."""

    def __init__(self):
        self.producer = None
        self.bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092'])
        self.topic = 'raw-logs'
        self.connect()

    def connect(self):
        """Establish connection with the Kafka broker."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all',
                retries=3,
                max_block_ms=2000  # Avoid blocking the Django thread too long
            )
            logger.info("Kafka Producer successfully connected to %s", self.bootstrap_servers)
        except KafkaError as e:
            logger.error("Failed to initialize Kafka Producer: %s", e)
            self.producer = None

    def publish_log(self, log_data):
        """Publish a single log dictionary to the Kafka topic."""
        if not self.producer:
            # Try to reconnect
            self.connect()
            if not self.producer:
                logger.error("Kafka Producer is offline. Dropping log publish.")
                return False

        try:
            future = self.producer.send(self.topic, log_data)
            # Asynchronous send, but we can verify success via callback in a production-grade setting
            # or blocks briefly on high-priority
            return True
        except KafkaError as e:
            logger.error("Failed to send message to Kafka: %s", e)
            return False

    def close(self):
        """Clean up the producer connection."""
        if self.producer:
            self.producer.close()
            logger.info("Kafka Producer connection closed.")
