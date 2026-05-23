import logging
import torch
import torch.nn as nn
import numpy as np

logger = logging.getLogger(__name__)


class LSTMAutoencoder(nn.Module):
    """PyTorch LSTM Autoencoder for temporal anomaly detection."""

    def __init__(self, input_dim=26, hidden_dim=16):
        super().__init__()
        # Encoder
        self.lstm1 = nn.LSTM(input_dim, hidden_dim, batch_first=True, num_layers=2)
        # Decoder
        self.lstm2 = nn.LSTM(hidden_dim, input_dim, batch_first=True, num_layers=2)

    def forward(self, x):
        # x shape: [batch, seq_len, input_dim]
        enc_out, _ = self.lstm1(x)
        dec_out, _ = self.lstm2(enc_out)
        return dec_out


class LSTMDetector:
    """LSTM-based sequence anomaly detector."""

    def __init__(self, input_dim=26, sequence_length=20):
        self.input_dim = input_dim
        self.sequence_length = sequence_length
        self.model = LSTMAutoencoder(input_dim)
        self.is_trained = False
        self.threshold = 0.5
        self.version = "1.0.0"
        self.metadata = {
            "algorithm": "LSTM Autoencoder",
            "sequence_length": sequence_length,
            "input_dim": input_dim,
        }

    def train(self, sequences, epochs=50, lr=0.001):
        """Train the autoencoder on normal sequence data."""
        logger.info("Training LSTM Autoencoder model...")
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        dataset = torch.tensor(sequences, dtype=torch.float32)

        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(dataset)
            loss = criterion(outputs, dataset)
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 10 == 0:
                logger.info("Epoch [%d/%d] Loss: %.4f", epoch + 1, epochs, loss.item())

        self.is_trained = True

        # Calibrate threshold
        self.model.eval()
        with torch.no_grad():
            preds = self.model(dataset)
            # Compute MSE per sequence
            errors = torch.mean((preds - dataset) ** 2, dim=(1, 2)).numpy()
            self.threshold = float(np.percentile(errors, 95))
            self.metadata["threshold"] = self.threshold

        logger.info("LSTM Autoencoder training complete. Threshold: %.4f", self.threshold)

    def predict(self, sequence):
        """
        Predict if a sequence of feature vectors is anomalous.
        sequence: list of shape (seq_len, 26) or list of lists.
        """
        if not self.is_trained:
            return {"reconstruction_error": 0.0, "is_anomaly": False, "threshold": self.threshold}

        self.model.eval()
        with torch.no_grad():
            # Pad or truncate to match sequence length
            seq_arr = np.array(sequence, dtype=np.float32)
            if seq_arr.shape[0] < self.sequence_length:
                # Pad with zeros
                pad_len = self.sequence_length - seq_arr.shape[0]
                pad_arr = np.zeros((pad_len, self.input_dim), dtype=np.float32)
                seq_arr = np.vstack([pad_arr, seq_arr])
            elif seq_arr.shape[0] > self.sequence_length:
                # Truncate
                seq_arr = seq_arr[-self.sequence_length :]

            x = torch.tensor(seq_arr, dtype=torch.float32).unsqueeze(0) # add batch dim
            pred = self.model(x)
            recon_error = float(torch.mean((pred - x) ** 2).item())
            is_anomaly = recon_error > self.threshold

            return {
                "reconstruction_error": recon_error,
                "is_anomaly": is_anomaly,
                "threshold": self.threshold,
            }

    def save(self, path):
        """Save model weights and state."""
        logger.info("Saving LSTM weights to %s", path)
        state = {
            "model_state": self.model.state_dict(),
            "threshold": self.threshold,
            "is_trained": self.is_trained,
            "version": self.version,
            "metadata": self.metadata,
        }
        torch.save(state, path)

    def load(self, path):
        """Load model weights and state."""
        logger.info("Loading LSTM weights from %s", path)
        state = torch.load(path, map_location=torch.device("cpu"))
        self.model.load_state_dict(state["model_state"])
        self.threshold = state["threshold"]
        self.is_trained = state["is_trained"]
        self.version = state["version"]
        self.metadata = state["metadata"]
