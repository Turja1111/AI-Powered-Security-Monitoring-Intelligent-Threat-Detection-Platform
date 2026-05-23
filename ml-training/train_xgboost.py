"""
Training script for XGBoost multi-class threat classifier.
"""
import os
import logging
import joblib
import numpy as np

from data_utils import generate_synthetic_data, extract_features_df
from mlflow_tracking import log_model_run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_xgboost")

MODEL_DIR = "../ml-service/model-artifacts"


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    logger.info("Generating synthetic multi-class training data...")
    raw_df = generate_synthetic_data(n_samples=8000, attack_ratio=0.15)

    logger.info("Extracting engineered feature vectors...")
    X, y_labels = extract_features_df(raw_df)

    # Load pre-trained scaler from step 1
    scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        X_scaled = scaler.transform(X)
        logger.info("Scaled features using pre-loaded scaler.")
    else:
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, scaler_path)
        logger.info("Scaler not found. Fit a new StandardScaler and saved it.")

    # Load xgboost classifier wrapper
    import sys
    sys.path.append("../ml-service")
    from models.xgboost_classifier import XGBoostClassifier

    xgb_wrapper = XGBoostClassifier()

    # Map y labels to indices
    # We must match XGBoostClassifier.ATTACK_CLASSES
    class_map = {name: i for i, name in enumerate(xgb_wrapper.ATTACK_CLASSES)}
    y_mapped = np.array([class_map.get(label, 0) for label in y_labels]) # fallback to BENIGN (0)

    logger.info("Training multi-class XGBoost classifier...")
    xgb_wrapper.train(X_scaled, y_mapped)

    # Save fitted model
    model_path = os.path.join(MODEL_DIR, "xgboost_classifier.joblib")
    xgb_wrapper.save(model_path)
    logger.info("Saved trained XGBoost classifier to %s", model_path)

    # Calculate micro F1 score
    from sklearn.metrics import f1_score
    preds = xgb_wrapper.model.predict(X_scaled)
    f1 = float(f1_score(y_mapped, preds, average="macro"))

    # Log to simulated MLflow registry
    metrics = {
        "f1_score": f1,
        "classes_count": len(xgb_wrapper.ATTACK_CLASSES),
    }
    log_model_run("xgboost_classifier", xgb_wrapper.version, metrics)


if __name__ == "__main__":
    main()
