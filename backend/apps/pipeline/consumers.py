import json
import logging
import threading
import time
import requests
from django.conf import settings
from django.utils import timezone
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from apps.ingestion.models import LogEntry
from apps.pipeline.models import FeatureVector
from apps.pipeline.feature_engineering import extract_features, get_feature_list
from apps.alerts.engine import AlertEngine

logger = logging.getLogger(__name__)

class SecurityLogKafkaConsumer(threading.Thread):
    """Kafka consumer thread that processes raw security logs and runs the ML pipeline."""

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = False
        self.bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092'])
        self.consumer_topic = 'raw-logs'
        self.producer_topic = 'scored-events'
        self.ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://localhost:8001/predict/ensemble')
        self.consumer = None
        self.producer = None
        self.alert_engine = AlertEngine()

    def connect_kafka(self):
        """Establish Kafka connections for consuming and producing."""
        # Connect Consumer
        while self.running and not self.consumer:
            try:
                self.consumer = KafkaConsumer(
                    self.consumer_topic,
                    bootstrap_servers=self.bootstrap_servers,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    group_id='security-pipeline-group',
                    auto_offset_reset='latest',
                    enable_auto_commit=True
                )
                logger.info("Kafka Pipeline Consumer successfully connected to %s", self.bootstrap_servers)
            except KafkaError as e:
                logger.error("Failed to connect consumer to Kafka. Retrying in 5s... Error: %s", e)
                time.sleep(5)

        # Connect Producer
        while self.running and not self.producer:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
                )
                logger.info("Kafka Pipeline Producer successfully connected to %s", self.bootstrap_servers)
            except KafkaError as e:
                logger.error("Failed to connect producer to Kafka. Retrying in 5s... Error: %s", e)
                time.sleep(5)

    def start_pipeline(self):
        """Start the consumer loop."""
        self.running = True
        self.start()

    def stop_pipeline(self):
        """Stop the consumer loop."""
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()

    def run(self):
        """Main consumer loop."""
        self.connect_kafka()
        
        while self.running:
            try:
                if not self.consumer or not self.producer:
                    self.connect_kafka()
                    if not self.running:
                        break

                message_pack = self.consumer.poll(timeout_ms=1000)
                for tp, messages in message_pack.items():
                    for message in messages:
                        if not self.running:
                            break
                        self.process_message(message.value)

            except Exception as e:
                logger.exception("Error in pipeline consumer run loop: %s", e)
                time.sleep(2)

    def process_message(self, log_dict):
        """Processes a single raw log from Kafka."""
        try:
            # 1. Ensure log is saved in DB if ingested via producer directly
            log_id = log_dict.get('id')
            if log_id:
                try:
                    log_entry = LogEntry.objects.get(id=log_id)
                except LogEntry.DoesNotExist:
                    # Save it if it is missing
                    log_entry = LogEntry.objects.create(
                        id=log_id,
                        timestamp=log_dict.get('timestamp', timezone.now()),
                        source_ip=log_dict.get('source_ip', '0.0.0.0'),
                        destination_ip=log_dict.get('destination_ip', '0.0.0.0'),
                        source_port=int(log_dict.get('source_port', 0)),
                        destination_port=int(log_dict.get('destination_port', 0)),
                        protocol=log_dict.get('protocol', 'TCP'),
                        bytes_sent=int(log_dict.get('bytes_sent', 0)),
                        bytes_received=int(log_dict.get('bytes_received', 0)),
                        duration_ms=int(log_dict.get('duration_ms', 0)),
                        packet_count=int(log_dict.get('packet_count', 0)),
                        tcp_flags=log_dict.get('tcp_flags', ''),
                        label=log_dict.get('label', 'BENIGN'),
                        source=log_dict.get('source', 'live')
                    )
            else:
                # Log without ID, skip or create with UUID
                return

            # 2. Trigger Feature Extraction for the last 5 minutes of this Source IP
            window_end = log_entry.timestamp
            window_start = window_end - timezone.timedelta(minutes=5)
            
            # Fetch all logs in the window for this source_ip
            logs_queryset = LogEntry.objects.filter(source_ip=log_entry.source_ip, timestamp__range=(window_start, window_end))
            feature_dict = extract_features(logs_queryset, window_start, window_end, log_entry.source_ip)
            feature_list = get_feature_list(feature_dict)

            # 3. Call ML service /predict/ensemble endpoint
            ml_results = self.score_feature_vector(feature_list)
            if not ml_results:
                logger.error("Failed to score feature vector for IP %s", log_entry.source_ip)
                return

            # 4. Save FeatureVector to DB
            fv_record = FeatureVector.objects.create(
                window_start=window_start,
                window_end=window_end,
                source_ip=log_entry.source_ip,
                feature_vector=feature_dict,
                anomaly_score=ml_results.get('anomaly_score', 0.0),
                predicted_label=ml_results.get('predicted_label', 'BENIGN'),
                confidence=ml_results.get('confidence', 1.0),
                computed_at=timezone.now()
            )

            # 5. Process in Alert Engine (severity, deduplication, notifications, WebSocket push)
            event_data = {
                "feature_vector_id": str(fv_record.id),
                "source_ip": fv_record.source_ip,
                "destination_ip": log_entry.destination_ip,
                "anomaly_score": fv_record.anomaly_score,
                "predicted_label": fv_record.predicted_label,
                "confidence": fv_record.confidence,
                "timestamp": fv_record.window_end.isoformat(),
                "raw_log_ids": [str(log_entry.id)]
            }
            self.alert_engine.process_scored_event(event_data)

            # 6. Publish to scored-events topic
            self.producer.send(self.producer_topic, event_data)

        except Exception as e:
            logger.exception("Failed to process pipeline message: %s", e)

    def score_feature_vector(self, feature_list):
        """Hits FastAPI ML Service to score the feature vector."""
        try:
            # The FastAPI ensemble endpoint expects {"feature_vector": [...]} or raw list
            # FastAPI prediction schema: ensemble endpoint takes feature_vector list or json dict
            payload = {"feature_vector": feature_list}
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(self.ml_service_url, json=payload, headers=headers, timeout=3.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("FastAPI returned error status %d: %s", response.status_code, response.text)
        except requests.RequestException as e:
            logger.error("FastAPI connection error: %s", e)
        return None
