import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """Ensemble prediction and severity classification pipeline."""

    def __init__(self, isolation_forest=None, xgboost_classifier=None, lstm_detector=None):
        self.isolation_forest = isolation_forest
        self.xgboost_classifier = xgboost_classifier
        self.lstm_detector = lstm_detector

    def predict_all(self, feature_vector: list[float], sequence: Optional[list[list[float]]] = None) -> dict:
        """
        Run all loaded models on the feature vector and combine results.
        """
        # 1. Unsupervised Isolation Forest
        if self.isolation_forest and self.isolation_forest.is_trained:
            if_res = self.isolation_forest.predict(feature_vector)
        else:
            if_res = {"anomaly_score": 0.0, "is_anomaly": False, "threshold": -0.4}

        # 2. Supervised XGBoost Classifier
        if self.xgboost_classifier and self.xgboost_classifier.is_trained:
            xgb_res = self.xgboost_classifier.predict(feature_vector)
            explain_res = self.xgboost_classifier.explain(feature_vector)
            xgb_res.update(explain_res)
        else:
            xgb_res = {
                "predicted_label": "BENIGN",
                "confidence": 1.0,
                "class_probabilities": {},
                "shap_values": {},
                "top_features": [],
            }

        # 3. PyTorch LSTM Autoencoder sequence detection (optional)
        lstm_res = None
        if self.lstm_detector and self.lstm_detector.is_trained and sequence:
            lstm_res = self.lstm_detector.predict(sequence)

        # 4. Ensemble Logic and Severity Classification
        if_score = if_res.get("anomaly_score", if_res.get("score", 0.0))
        xgb_label = xgb_res.get("predicted_label", "BENIGN")
        xgb_conf = xgb_res.get("confidence", 0.0)

        final_severity = self.calculate_final_severity(if_score, xgb_conf, xgb_label)
        is_threat = final_severity != "LOW"

        # Final confidence is a blend of models
        confidence = xgb_conf if is_threat else (1.0 - xgb_conf)

        return {
            "isolation_forest": if_res,
            "xgboost": xgb_res,
            "lstm": lstm_res,
            "final_severity": final_severity,
            "is_threat": is_threat,
            "confidence": confidence,
        }

    def calculate_final_severity(self, if_score: float, xgb_confidence: float, xgb_label: str) -> str:
        """
        Combine anomaly score and classifier confidence to assign severity.
        """
        label_lower = xgb_label.lower()

        # BENIGN defaults
        if label_lower == "benign" and if_score > -0.3:
            return "LOW"

        # CRITICAL: highly anomalous, high confidence, severe class
        if (
            if_score < -0.7
            and xgb_confidence > 0.95
            and any(term in label_lower for term in ["ddos", "infiltration", "exfiltration"])
        ):
            return "CRITICAL"

        # HIGH: high confidence attack class
        if xgb_confidence > 0.85 and label_lower != "benign":
            return "HIGH"

        # MEDIUM: borderline anomaly or medium confidence attack
        if if_score < -0.4 or (xgb_confidence > 0.60 and label_lower != "benign"):
            return "MEDIUM"

        # LOW: borderline anomaly, no active attack signature
        if if_score < -0.2:
            return "LOW"

        return "LOW"

    def models_status(self) -> dict:
        """Return loading and training status of each model in the ensemble."""
        return {
            "isolation_forest": {
                "loaded": self.isolation_forest is not None,
                "trained": getattr(self.isolation_forest, "is_trained", False),
            },
            "xgboost": {
                "loaded": self.xgboost_classifier is not None,
                "trained": getattr(self.xgboost_classifier, "is_trained", False),
            },
            "lstm": {
                "loaded": self.lstm_detector is not None,
                "trained": getattr(self.lstm_detector, "is_trained", False),
            },
        }
