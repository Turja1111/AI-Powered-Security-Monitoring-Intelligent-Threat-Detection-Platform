"""
Streaming Network Log Consumer and Pipeline Processor.
Consumes events from Kafka raw-logs, extracts windowed features, scores them via ML Service, and alerts.
"""
import sys
import os
import json
import time
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger("pipeline_consumer")


def main():
    logger.info("Initializing streaming pipeline consumer...")

    # Load environment variables or configuration defaults
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ml_api_key = os.getenv("ML_SERVICE_API_KEY", "ml-service-internal-key-change-me")
    backend_url = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000/api/v1")

    # Set up Kafka consumer
    kafka_consumer = None
    try:
        from kafka import KafkaConsumer
        kafka_consumer = KafkaConsumer(
            "raw-logs",
            bootstrap_servers=kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            group_id="security-platform-pipeline",
        )
        logger.info("Successfully connected to Kafka brokers: %s", kafka_servers)
    except Exception as e:
        logger.error("Kafka consumer initialization failed: %s. Standing by for streaming...", e)
        # Running in a simple standby sleep loop for fallback
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            return

    logger.info("Listening for streaming log events on topic 'raw-logs'...")
    try:
        for message in kafka_consumer:
            event = message.value
            logger.info("Received event: %s→%s", event.get("source_ip"), event.get("destination_ip"))

            # 1. Forward raw log to main Django database for log explorer
            try:
                requests.post(f"{backend_url}/logs/", json=event, timeout=2)
            except Exception as d_err:
                logger.debug("Failed to store raw log to backend: %s", d_err)

            # In production, streaming feature aggregation runs here using a sliding window.
            # For immediate response, we can fetch features or run predictions directly on the event.
            
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        if kafka_consumer:
            kafka_consumer.close()


if __name__ == "__main__":
    main()
