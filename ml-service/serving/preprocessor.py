import logging
import joblib
import numpy as np

logger = logging.getLogger(__name__)


class Preprocessor:
    """Feature validation, missing values imputation, and normalization scaler."""

    FEATURE_NAMES = [
        "total_bytes_sent",
        "total_bytes_received",
        "total_packets",
        "avg_packet_size",
        "connection_count",
        "unique_dest_ips",
        "unique_dest_ports",
        "tcp_ratio",
        "udp_ratio",
        "icmp_ratio",
        "port_entropy",
        "avg_duration_ms",
        "bytes_per_packet",
        "connections_per_sec",
        "inter_arrival_mean",
        "inter_arrival_std",
        "night_time_flag",
        "byte_asymmetry_ratio",
        "failed_connection_ratio",
        "syn_flag_ratio",
        "ack_flag_ratio",
        "fin_flag_ratio",
        "rst_flag_ratio",
        "psh_flag_ratio",
        "urg_flag_ratio",
        "dns_query_ratio",
    ]

    def __init__(self):
        self.scaler = None
        self.scaler_loaded = False

    def load_scaler(self, path):
        """Load fitted StandardScaler from joblib."""
        try:
            logger.info("Loading preprocessor scaler from %s", path)
            self.scaler = joblib.load(path)
            self.scaler_loaded = True
        except Exception as e:
            logger.error("Failed to load scaler: %s", e)
            self.scaler_loaded = False

    def validate_features(self, feature_dict):
        """Ensure all 26 feature keys are present."""
        for name in self.FEATURE_NAMES:
            if name not in feature_dict:
                logger.debug("Feature %s is missing, filling with 0.0", name)
                feature_dict[name] = 0.0
        return feature_dict

    def handle_missing_values(self, feature_dict):
        """Fill NaNs, None, or infinite values with safe floats."""
        for name in self.FEATURE_NAMES:
            val = feature_dict.get(name, 0.0)
            if val is None or np.isnan(val) or np.isinf(val):
                feature_dict[name] = 0.0
        return feature_dict

    def transform(self, raw_features_dict):
        """
        Validate, clean, and normalize the features.
        Returns: numpy array of shape (26,)
        """
        validated = self.validate_features(raw_features_dict)
        cleaned = self.handle_missing_values(validated)

        # Convert to list ordered by FEATURE_NAMES
        ordered_list = [float(cleaned[name]) for name in self.FEATURE_NAMES]
        arr = np.array(ordered_list).reshape(1, -1)

        # Scale features if scaler is loaded
        if self.scaler_loaded and self.scaler:
            try:
                arr = self.scaler.transform(arr)
            except Exception as e:
                logger.error("Scaling error: %s. Using unscaled raw features.", e)

        return arr.flatten()
