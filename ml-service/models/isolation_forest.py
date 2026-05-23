import logging
import joblib
from sklearn.ensemble import IsolationForest
import numpy as np

logger = logging.getLogger(__name__)


class IsolationForestModel:
    """Unsupervised Isolation Forest anomaly detection model."""

    def __init__(self):
        self.model = None
        self.is_trained = False
        self.threshold = -0.4
        self.version = "1.0.0"
        self.metadata = {
            "algorithm": "Isolation Forest",
            "n_estimators": 200,
            "contamination": 0.05,
        }

    def train(self, X, contamination=0.05, n_estimators=200):
        """Train isolation forest on a clean dataset of normal traffic."""
        logger.info("Training Isolation Forest model with n_estimators=%d", n_estimators)
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X)
        self.is_trained = True

        # Calibrate a realistic decision threshold
        scores = self.model.score_samples(X)
        self.threshold = float(np.percentile(scores, contamination * 100))
        self.metadata["threshold"] = self.threshold
        logger.info("Isolation Forest training complete. Calibrated threshold: %.3f", self.threshold)

    def predict(self, feature_vector):
        """
        Run inference on a single feature vector.
        Returns: {score: float, is_anomaly: bool, threshold: float}
        """
        if not self.is_trained or not self.model:
            # Untrained fallback
            return {"score": 0.0, "is_anomaly": False, "threshold": self.threshold}

        X = np.array(feature_vector).reshape(1, -1)
        score = float(self.model.score_samples(X)[0])
        is_anomaly = score < self.threshold
        return {
            "score": score,
            "is_anomaly": is_anomaly,
            "threshold": self.threshold,
        }

    def save(self, path):
        """Save fitted model and metadata to disk."""
        logger.info("Saving Isolation Forest to %s", path)
        data = {
            "model": self.model,
            "threshold": self.threshold,
            "version": self.version,
            "metadata": self.metadata,
            "is_trained": self.is_trained,
        }
        joblib.dump(data, path)

    def load(self, path):
        """Load fitted model and metadata from disk."""
        logger.info("Loading Isolation Forest from %s", path)
        data = joblib.load(path)
        self.model = data["model"]
        self.threshold = data["threshold"]
        self.version = data["version"]
        self.metadata = data["metadata"]
        self.is_trained = data["is_trained"]
