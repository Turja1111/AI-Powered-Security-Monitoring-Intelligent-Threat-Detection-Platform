"""
Alert Engine — severity classification, deduplication, and notification dispatch.
"""
import hashlib
import json
import logging
from typing import Optional

import redis
import requests
from django.conf import settings
from django.utils import timezone

from .models import Alert

logger = logging.getLogger(__name__)


class AlertEngine:
    """Core alert processing engine with severity classification and dedup."""

    SEVERITY_THRESHOLDS = {
        "CRITICAL": {"if_score": -0.7, "xgb_confidence": 0.95, "labels": ["DDoS", "Infiltration", "exfiltration"]},
        "HIGH": {"xgb_confidence": 0.85},
        "MEDIUM": {"if_score": -0.4, "xgb_confidence": 0.60},
        "LOW": {"if_score": -0.2},
    }

    def __init__(self):
        try:
            self._redis = redis.Redis.from_url(
                getattr(settings, "REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True,
            )
            self._redis.ping()
        except Exception:
            logger.warning("Redis unavailable — deduplication disabled")
            self._redis = None

    def classify_severity(
        self, anomaly_score: float, xgb_confidence: float, predicted_label: str
    ) -> str:
        """Classify alert severity based on model outputs."""
        label_lower = predicted_label.lower()

        # CRITICAL
        critical = self.SEVERITY_THRESHOLDS["CRITICAL"]
        if (
            anomaly_score < critical["if_score"]
            and xgb_confidence > critical["xgb_confidence"]
            and any(l.lower() in label_lower for l in critical["labels"])
        ):
            return "CRITICAL"

        # HIGH
        if xgb_confidence > self.SEVERITY_THRESHOLDS["HIGH"]["xgb_confidence"]:
            if label_lower != "benign":
                return "HIGH"

        # MEDIUM
        medium = self.SEVERITY_THRESHOLDS["MEDIUM"]
        if anomaly_score < medium["if_score"] or xgb_confidence > medium["xgb_confidence"]:
            return "MEDIUM"

        # LOW
        if anomaly_score < self.SEVERITY_THRESHOLDS["LOW"]["if_score"]:
            return "LOW"

        return "LOW"

    def _dedup_key(self, source_ip: str, alert_type: str, severity: str) -> str:
        """Generate Redis deduplication key."""
        return f"alert:dedup:{source_ip}:{alert_type}:{severity}"

    def is_duplicate(self, source_ip: str, alert_type: str, severity: str) -> bool:
        """Check if alert is a duplicate using Redis TTL-based dedup."""
        if not self._redis:
            return False

        key = self._dedup_key(source_ip, alert_type, severity)
        try:
            if self._redis.exists(key):
                self._redis.incr(f"{key}:count")
                return True

            # Set key with severity-appropriate TTL
            ttl = settings.ALERT_DEDUP_TTL_SECONDS.get(severity, 300)
            self._redis.setex(key, ttl, "1")
            self._redis.setex(f"{key}:count", ttl, "1")
            return False
        except Exception as e:
            logger.error("Redis dedup error: %s", e)
            return False

    def _map_label_to_alert_type(self, label: str) -> str:
        """Map ML predicted label to alert_type."""
        label_map = {
            "ddos": "ddos",
            "portscan": "port_scan",
            "port_scan": "port_scan",
            "bruteforce": "brute_force",
            "brute_force": "brute_force",
            "ftp-patator": "brute_force",
            "ssh-patator": "brute_force",
            "webattack": "web_attack",
            "web_attack": "web_attack",
            "infiltration": "infiltration",
            "bot": "bot",
            "dos-slowloris": "dos_slowloris",
            "dos-hulk": "dos_hulk",
            "dos-goldeneye": "ddos",
            "dos-slowhttptest": "dos_slowloris",
            "heartbleed": "heartbleed",
            "exfiltration": "exfiltration",
        }
        normalized = label.lower().replace(" ", "").replace("-", "").replace("_", "")
        for key, value in label_map.items():
            if key.replace("-", "").replace("_", "") in normalized:
                return value
        return "anomaly"

    def create_alert(
        self,
        source_ip: str,
        destination_ip: str,
        anomaly_score: float,
        xgb_confidence: float,
        predicted_label: str,
        model_used: str = "ensemble",
        raw_log_ids: Optional[list] = None,
        description: str = "",
    ) -> Optional[Alert]:
        """Create an alert if not a duplicate. Returns Alert or None."""
        severity = self.classify_severity(anomaly_score, xgb_confidence, predicted_label)
        alert_type = self._map_label_to_alert_type(predicted_label)

        # Skip BENIGN predictions
        if predicted_label.lower() == "benign" and anomaly_score > -0.2:
            return None

        # Dedup check
        if self.is_duplicate(source_ip, alert_type, severity):
            logger.debug("Alert deduplicated: %s/%s/%s", source_ip, alert_type, severity)
            return None

        if not description:
            description = (
                f"Detected {predicted_label} activity from {source_ip}. "
                f"Anomaly score: {anomaly_score:.3f}, Confidence: {xgb_confidence:.1%}"
            )

        alert = Alert.objects.create(
            severity=severity,
            alert_type=alert_type,
            source_ip=source_ip,
            destination_ip=destination_ip,
            anomaly_score=anomaly_score,
            model_used=model_used,
            description=description,
            predicted_label=predicted_label,
            confidence=xgb_confidence,
            raw_log_ids=raw_log_ids or [],
        )

        logger.info("Alert created: %s [%s] %s from %s", alert.id, severity, alert_type, source_ip)

        # Send notifications for HIGH+ severity
        if severity in ("HIGH", "CRITICAL"):
            self._send_notifications(alert)

        return alert

    def _send_notifications(self, alert: Alert):
        """Send Slack/email notifications for high-severity alerts."""
        # Slack webhook
        webhook_url = getattr(settings, "SLACK_WEBHOOK_URL", "")
        if webhook_url:
            try:
                payload = {
                    "text": f"🚨 *{alert.severity} ALERT* — {alert.alert_type}",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*Severity:* {alert.severity}\n"
                                    f"*Type:* {alert.alert_type}\n"
                                    f"*Source IP:* `{alert.source_ip}`\n"
                                    f"*Confidence:* {alert.confidence:.1%}\n"
                                    f"*Score:* {alert.anomaly_score:.3f}\n"
                                    f"*Description:* {alert.description}"
                                ),
                            },
                        }
                    ],
                }
                requests.post(webhook_url, json=payload, timeout=5)
            except Exception as e:
                logger.error("Slack notification failed: %s", e)

    def process_scored_event(self, event_data: dict) -> Optional[Alert]:
        """Main entry point: process a scored event from the ML pipeline."""
        return self.create_alert(
            source_ip=event_data.get("source_ip", "0.0.0.0"),
            destination_ip=event_data.get("destination_ip", "0.0.0.0"),
            anomaly_score=event_data.get("anomaly_score", 0.0),
            xgb_confidence=event_data.get("confidence", 0.0),
            predicted_label=event_data.get("predicted_label", "anomaly"),
            model_used=event_data.get("model_used", "ensemble"),
            raw_log_ids=event_data.get("raw_log_ids", []),
        )
