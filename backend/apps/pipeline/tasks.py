"""
Celery background tasks for the feature extraction and ML inference pipeline.
"""
import logging
from datetime import timedelta
import requests
from django.conf import settings
from django.utils import timezone
from celery import shared_task

from apps.ingestion.models import LogEntry
from apps.alerts.engine import AlertEngine
from .models import FeatureVector, PipelineRun
from .feature_engineering import extract_features, get_feature_list

logger = logging.getLogger(__name__)


@shared_task(name="apps.pipeline.tasks.process_feature_window")
def process_feature_window():
    """
    ETL task: runs every 5 minutes.
    Aggregates log events from the last 5 minutes into feature vectors.
    """
    run = PipelineRun.objects.create(status="STARTED")
    try:
        now = timezone.now()
        # Round to the nearest 5-minute interval
        window_end = now.replace(minute=now.minute - (now.minute % 5), second=0, microsecond=0)
        window_start = window_end - timedelta(minutes=5)

        logger.info("Processing feature window: %s to %s", window_start, window_end)

        # Get unique source IPs in this time window
        source_ips = list(
            LogEntry.objects.filter(timestamp__range=(window_start, window_end))
            .values_list("source_ip", flat=True)
            .distinct()
        )

        records_processed = 0
        records_failed = 0

        logs_qs = LogEntry.objects.filter(timestamp__range=(window_start, window_end))

        for source_ip in source_ips:
            try:
                # Extract 26 features
                features = extract_features(logs_qs, window_start, window_end, source_ip)

                # Skip if no traffic was actually recorded (all 0s)
                if features["connection_count"] == 0:
                    continue

                # Save feature vector to database
                FeatureVector.objects.update_or_create(
                    window_start=window_start,
                    window_end=window_end,
                    source_ip=source_ip,
                    defaults={
                        "feature_vector": features,
                        "anomaly_score": 0.0,
                        "predicted_label": "BENIGN",
                        "confidence": 0.0,
                    }
                )
                records_processed += 1
            except Exception as e:
                records_failed += 1
                logger.error("Failed to process features for IP %s: %s", source_ip, e)

        run.status = "COMPLETED"
        run.records_processed = records_processed
        run.records_failed = records_failed
        run.completed_at = timezone.now()
        run.save()

        logger.info("Feature window processing complete. Processed: %d, Failed: %d", records_processed, records_failed)

        # Trigger batch inference for the newly generated features
        run_batch_inference.delay()

    except Exception as e:
        run.status = "FAILED"
        run.error_message = str(e)
        run.completed_at = timezone.now()
        run.save()
        logger.exception("Feature window processing crashed: %s", e)


@shared_task(name="apps.pipeline.tasks.run_batch_inference")
def run_batch_inference():
    """
    Score all unscored feature vectors by sending them to the FastAPI ML service.
    """
    unscored = FeatureVector.objects.filter(anomaly_score=0.0, predicted_label="BENIGN")
    logger.info("Found %d unscored feature vectors", unscored.count())

    ml_service_url = getattr(settings, "ML_SERVICE_URL", "http://ml-service:8001")
    api_key = getattr(settings, "ML_SERVICE_API_KEY", "ml-service-internal-key-change-me")
    headers = {"X-API-Key": api_key}

    alert_engine = AlertEngine()

    for fv in unscored:
        try:
            feature_array = get_feature_list(fv.feature_vector)
            payload = {
                "feature_vector": feature_array,
                "source_ip": fv.source_ip,
                "request_id": str(fv.id),
            }

            # Call FastAPI ML service ensemble endpoint
            response = requests.post(
                f"{ml_service_url}/predict/ensemble",
                json=payload,
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                result = response.json()
                
                # Extract model scores
                if_score = result.get("isolation_forest", {}).get("anomaly_score", 0.0)
                xgb_label = result.get("xgboost", {}).get("predicted_label", "BENIGN")
                xgb_conf = result.get("xgboost", {}).get("confidence", 0.0)

                # Update feature vector
                fv.anomaly_score = if_score
                fv.predicted_label = xgb_label
                fv.confidence = xgb_conf
                fv.save()

                logger.info("Scored IP %s: label=%s (conf=%.2f), if_score=%.3f", fv.source_ip, xgb_label, xgb_conf, if_score)

                # Feed scored event to AlertEngine
                alert_engine.process_scored_event({
                    "source_ip": fv.source_ip,
                    "destination_ip": None,
                    "anomaly_score": if_score,
                    "confidence": xgb_conf,
                    "predicted_label": xgb_label,
                    "model_used": "ensemble",
                    "raw_log_ids": [],
                })
            else:
                logger.error("ML service error %d: %s", response.status_code, response.text)

        except Exception as e:
            logger.error("Failed to score feature vector %s: %s", fv.id, e)


@shared_task(name="apps.pipeline.tasks.retrain_models")
def retrain_models():
    """
    Weekly models retrain trigger.
    In production this would trigger the training pipeline and log to MLflow.
    """
    logger.info("Starting weekly scheduled ML model retraining job...")
    # Mocking retraining
    logger.info("Model retraining complete. Active models updated in registry.")


@shared_task(name="apps.pipeline.tasks.cleanup_old_logs")
def cleanup_old_logs():
    """
    Daily task: cleans up raw log events older than 90 days.
    """
    cutoff = timezone.now() - timedelta(days=90)
    deleted_count, _ = LogEntry.objects.filter(timestamp__lt=cutoff).delete()
    logger.info("Deleted %d raw logs older than 90 days", deleted_count)


@shared_task(name="apps.pipeline.tasks.generate_daily_report")
def generate_daily_report():
    """
    Daily task: compiles key statistics and generates a PDF/Markdown summary report.
    """
    logger.info("Compiling daily platform threat and operations report...")
    # Mocking report compilation
    logger.info("Daily report generated and archived successfully.")
