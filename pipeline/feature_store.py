"""
Feature store abstraction layer for retrieving and managing historic window vectors.
"""
import logging
from datetime import datetime

logger = logging.getLogger("feature_store")


class FeatureStore:
    """Feature store management for LSTM sequences and ML analytics."""

    def __init__(self):
        # Dynamically load Django models if available
        self.FeatureVector = None
        try:
            import os
            import sys
            sys.path.append("../backend")
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
            import django
            django.setup()
            from apps.pipeline.models import FeatureVector
            self.FeatureVector = FeatureVector
            logger.info("FeatureStore successfully linked to Django PostgreSQL database.")
        except Exception as e:
            logger.warning("FeatureStore could not link to Django database context: %s. Using mock cache.", e)

    def save_feature_vector(self, source_ip, window_start, window_end, features):
        """Save a new computed feature vector to the features store table."""
        if not self.FeatureVector:
            logger.debug("FeatureStore DB offline. Feature vector cache bypassed.")
            return None
        try:
            obj, created = self.FeatureVector.objects.update_or_create(
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
            return obj
        except Exception as e:
            logger.error("Failed to save feature vector: %s", e)
            return None

    def get_recent_features(self, source_ip, n_windows=20):
        """
        Retrieve the last N feature windows for a source IP.
        Used to feed PyTorch LSTM sequence predictions.
        """
        if not self.FeatureVector:
            # Fallback mock sequence (20 windows of 26 features)
            return [ [0.0] * 26 for _ in range(n_windows) ]
        try:
            qs = self.FeatureVector.objects.filter(source_ip=source_ip).order_by("-window_end")[:n_windows]
            # Convert to float list of vectors in correct chronological order
            vectors = []
            for fv in reversed(qs):
                vector = [float(fv.feature_vector.get(name, 0.0)) for name in fv.feature_vector.keys()]
                vectors.append(vector)
            
            # Pad sequence if not long enough
            while len(vectors) < n_windows:
                vectors.insert(0, [0.0] * 26)
            return vectors
        except Exception as e:
            logger.error("Failed to retrieve recent features: %s", e)
            return [ [0.0] * 26 for _ in range(n_windows) ]

    def get_unscored_features(self, limit=100):
        """Get unscored feature rows for batch scoring."""
        if not self.FeatureVector:
            return []
        try:
            return list(self.FeatureVector.objects.filter(anomaly_score=0.0, predicted_label="BENIGN")[:limit])
        except Exception as e:
            logger.error("Failed to fetch unscored features: %s", e)
            return []

    def mark_as_scored(self, feature_id, anomaly_score, predicted_label, confidence):
        """Update inference outputs back into the store."""
        if not self.FeatureVector:
            return False
        try:
            self.FeatureVector.objects.filter(id=feature_id).update(
                anomaly_score=anomaly_score,
                predicted_label=predicted_label,
                confidence=confidence,
            )
            return True
        except Exception as e:
            logger.error("Failed to mark feature vector as scored: %s", e)
            return False
