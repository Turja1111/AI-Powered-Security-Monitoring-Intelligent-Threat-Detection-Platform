"""
Training script for the PyTorch LSTM Autoencoder sequence threat detector.
"""
import os
import logging
import joblib
import numpy as np

from data_utils import generate_synthetic_data, extract_features_df
from mlflow_tracking import log_model_run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_lstm")

MODEL_DIR = "../ml-service/model-artifacts"
SEQUENCE_LENGTH = 20
INPUT_DIM = 26


def create_sequences(X, seq_length):
    """Segment data into overlapping sequences of seq_length."""
    sequences = []
    for i in range(len(X) - seq_length + 1):
        sequences.append(X[i : i + seq_length])
    return np.array(sequences)


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    logger.info("Generating synthetic normal sequence data...")
    # Clean normal baseline sequence data
    raw_df = generate_synthetic_data(n_samples=3000, attack_ratio=0.0)

    logger.info("Extracting feature vectors...")
    X, _ = extract_features_df(raw_df)

    # Scale features
    scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        X_scaled = scaler.transform(X)
    else:
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, scaler_path)

    # Segment into sequences
    logger.info("Segmenting into temporal sequences of length %d...", SEQUENCE_LENGTH)
    sequences = create_sequences(X_scaled, SEQUENCE_LENGTH)

    if len(sequences) == 0:
        logger.error("Not enough data to segment into sequences! Generating fake sequences for fallback.")
        sequences = np.random.randn(10, SEQUENCE_LENGTH, INPUT_DIM)

    # Import PyTorch detector wrapper
    import sys
    sys.path.append("../ml-service")
    from models.lstm_detector import LSTMDetector

    lstm_wrapper = LSTMDetector(input_dim=INPUT_DIM, sequence_length=SEQUENCE_LENGTH)
    
    logger.info("Training LSTM Autoencoder...")
    lstm_wrapper.train(sequences, epochs=15, lr=0.001)

    # Save fitted model weights
    model_path = os.path.join(MODEL_DIR, "lstm_detector.pt")
    lstm_wrapper.save(model_path)
    logger.info("Saved trained LSTM model to %s", model_path)

    # Log to simulated MLflow registry
    metrics = {
        "sequence_length": SEQUENCE_LENGTH,
        "calibrated_threshold": lstm_wrapper.threshold,
    }
    log_model_run("lstm_detector", lstm_wrapper.version, metrics)


if __name__ == "__main__":
    main()
