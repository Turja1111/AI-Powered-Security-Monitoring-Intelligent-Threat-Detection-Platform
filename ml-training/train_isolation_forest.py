"""
Training script for Isolation Forest (unsupervised anomaly detector).
"""
import os
import logging
import joblib
from sklearn.preprocessing import StandardScaler

from data_utils import generate_synthetic_data, extract_features_df
from mlflow_tracking import log_model_run  # We will implement this next

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_isolation_forest")

MODEL_DIR = "../ml-service/model-artifacts"


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    logger.info("Generating synthetic training data...")
    raw_df = generate_synthetic_data(n_samples=5000, attack_ratio=0.0)  # Pure normal traffic for unsupervised baseline

    logger.info("Extracting engineered feature vectors from raw logs...")
    X, y = extract_features_df(raw_df)

    logger.info("Fitting StandardScaler on baseline normal traffic...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Save fitted scaler
    scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
    joblib.dump(scaler, scaler_path)
    logger.info("Saved fitted scaler to %s", scaler_path)

    # Import model wrapper and train
    # Since we need to save the model to ml-service/model-artifacts, let's train it
    from sys import path
    path.append("../ml-service")
    from models.isolation_forest import IsolationForestModel

    if_model = IsolationForestModel()
    if_model.train(X_scaled, contamination=0.05, n_estimators=200)

    # Save fitted model
    model_path = os.path.join(MODEL_DIR, "isolation_forest.joblib")
    if_model.save(model_path)
    logger.info("Saved trained IsolationForest model to %s", model_path)

    # Log to simulated MLflow registry
    metrics = {
        "contamination": 0.05,
        "n_estimators": 200,
        "calibrated_threshold": if_model.threshold,
    }
    log_model_run("isolation_forest", if_model.version, metrics)


if __name__ == "__main__":
    main()
