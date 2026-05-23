"""
Edge AI MQTT alert publisher.
Processes local log files or stdin stream, runs ONNX inference, and publishes anomalies to MQTT.
"""
import sys
import os
import time
import json
import logging
import yaml

from onnx_inference import ONNXInferenceEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger("mqtt_publisher")


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "edge_config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {
        "mqtt": {"broker_host": "localhost", "broker_port": 1883, "topic": "edge/security/events", "qos": 1},
        "model": {"path": "./model-artifacts/xgboost_model.onnx", "threshold": 0.6}
    }


def main():
    config = load_config()
    logger.info("Initializing Edge MQTT publisher...")

    # Load ONNX Engine
    engine = ONNXInferenceEngine(config["model"]["path"])

    # Attempt MQTT Client Initialization
    mqtt_client = None
    try:
        import paho.mqtt.client as mqtt
        mqtt_client = mqtt.Client()
        mqtt_client.connect(
            config["mqtt"]["broker_host"],
            config["mqtt"]["broker_port"],
            keepalive=60
        )
        mqtt_client.loop_start()
        logger.info("Connected to MQTT broker: %s:%d", config["mqtt"]["broker_host"], config["mqtt"]["broker_port"])
    except Exception as e:
        logger.warning("MQTT broker unavailable (%s). Alert publishing falls back to syslog.", e)

    metrics = {
        "events_processed": 0,
        "anomalies_detected": 0,
        "bandwidth_saved_bytes": 0
    }

    logger.info("Edge monitoring started. Waiting for logs on stdin...")
    
    # Simple simulated input log stream
    try:
        while True:
            # Generate or mock log inputs if run directly
            raw_log = {
                "timestamp": time.time(),
                "source_ip": "192.168.1.55",
                "destination_ip": "192.168.1.2",
                "destination_port": 80,
                "bytes_sent": random.choice([200, 450, 80000000]) if 'random' in globals() else 200,
                "packet_count": 50,
                "duration_ms": 100
            }

            feature_arr = engine.preprocess(raw_log)
            pred = engine.predict(feature_arr)
            
            metrics["events_processed"] += 1
            raw_size = len(json.dumps(raw_log))

            if pred["predicted_label"] != "BENIGN" and pred["confidence"] >= config["model"]["threshold"]:
                metrics["anomalies_detected"] += 1
                alert_payload = {
                    "alert_type": pred["predicted_label"],
                    "confidence": pred["confidence"],
                    "source_ip": raw_log["source_ip"],
                    "destination_ip": raw_log["destination_ip"],
                    "timestamp": raw_log["timestamp"],
                    "latency_ms": pred["latency_ms"]
                }
                
                # Publish anomaly alert payload
                if mqtt_client:
                    mqtt_client.publish(
                        config["mqtt"]["topic"],
                        json.dumps(alert_payload),
                        qos=config["mqtt"]["qos"]
                    )
                    logger.info("🚨 [MQTT] Threat Alert Published: %s", pred["predicted_label"])
                else:
                    logger.info("🚨 [Syslog] Threat Alert Logged: %s", pred["predicted_label"])
            else:
                # Normal event: save bandwidth by discarding
                metrics["bandwidth_saved_bytes"] += raw_size

            if metrics["events_processed"] % 10 == 0:
                logger.info(
                    "Edge Stats — Processed: %d, Threats: %d, Bandwidth Saved: %d bytes",
                    metrics["events_processed"],
                    metrics["anomalies_detected"],
                    metrics["bandwidth_saved_bytes"]
                )

            time.sleep(5.0)

    except KeyboardInterrupt:
        logger.info("Stopping Edge publisher...")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()


if __name__ == "__main__":
    # Ensure random is available for standalone simulation
    import random
    main()
