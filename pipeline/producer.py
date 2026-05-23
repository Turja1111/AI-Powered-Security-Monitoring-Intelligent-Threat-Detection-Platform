"""
Synthetic Network Log Ingestion Producer.
Simulates high-velocity network log streams and publishes to Apache Kafka or raw REST ingestion endpoints.
"""
import sys
import os
import time
import json
import random
import logging
import argparse
from datetime import datetime
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger("ingestion_producer")


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Security Ingestion Stream Producer")
    parser.add_argument("--mode", type=str, choices=["synthetic", "replay"], default="synthetic", help="Ingestion mode")
    parser.add_argument("--attack-rate", type=float, default=0.10, help="Ratio of simulated attack traffic (0.0 to 1.0)")
    parser.add_argument("--dest-url", type=str, default="http://localhost:8000/api/v1/logs/", help="Django raw log ingestion REST url")
    parser.add_argument("--speed", type=float, default=1.0, help="Sleep duration between requests in seconds")
    return parser.parse_args()


def simulate_network_event(attack_rate=0.10):
    """Generate a high-fidelity raw network connection event."""
    # Pre-generate some IPs
    benign_ips = [f"192.168.1.{i}" for i in range(10, 100)]
    attacker_ips = ["10.0.0.1", "10.0.0.2", "172.16.0.5", "172.16.0.6"]
    server_ips = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]

    is_attack = random.random() < attack_rate
    protocol = random.choice(["TCP", "UDP", "ICMP"])
    timestamp = datetime.utcnow().isoformat() + "Z"

    if not is_attack:
        # BENIGN
        src_ip = random.choice(benign_ips)
        dst_ip = random.choice(server_ips)
        label = "BENIGN"

        if protocol == "ICMP":
            src_port = 0
            dst_port = 0
            bytes_sent = 64
            bytes_received = 64
            duration = 1
            packets = 1
            tcp_flags = ""
        elif protocol == "UDP":
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([53, 123, 161])
            bytes_sent = random.randint(50, 500)
            bytes_received = random.randint(50, 1000)
            duration = random.randint(5, 100)
            packets = random.randint(2, 10)
            tcp_flags = ""
        else:
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([80, 443, 8080])
            bytes_sent = random.randint(500, 50000)
            bytes_received = random.randint(1000, 500000)
            duration = random.randint(50, 5000)
            packets = random.randint(10, 100)
            tcp_flags = "A"
    else:
        # Attack simulation
        src_ip = random.choice(attacker_ips)
        dst_ip = random.choice(server_ips)
        attack_type = random.choice(["PortScan", "DDoS", "BruteForce", "Exfiltration"])
        label = attack_type

        if attack_type == "PortScan":
            protocol = "TCP"
            src_port = random.randint(40000, 60000)
            dst_port = random.randint(1, 1024)
            bytes_sent = 40
            bytes_received = 0
            duration = 10
            packets = 1
            tcp_flags = "S"
        elif attack_type == "DDoS":
            protocol = "TCP"
            src_port = random.randint(10000, 65535)
            dst_port = 80
            bytes_sent = 120
            bytes_received = 60
            duration = 5
            packets = 3
            tcp_flags = "S"
        elif attack_type == "BruteForce":
            protocol = "TCP"
            src_port = random.randint(30000, 50000)
            dst_port = random.choice([22, 3389])
            bytes_sent = random.randint(300, 800)
            bytes_received = random.randint(300, 600)
            duration = random.randint(100, 1000)
            packets = random.randint(5, 12)
            tcp_flags = "PA"
        else: # Exfiltration
            protocol = "TCP"
            src_port = random.randint(50000, 60000)
            dst_port = 443
            bytes_sent = random.randint(10000000, 100000000)
            bytes_received = random.randint(10000, 50000)
            duration = random.randint(60000, 300000)
            packets = random.randint(5000, 20000)
            tcp_flags = "A"

    return {
        "timestamp": timestamp,
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "source_port": src_port,
        "destination_port": dst_port,
        "protocol": protocol,
        "bytes_sent": bytes_sent,
        "bytes_received": bytes_received,
        "duration_ms": duration,
        "packet_count": packets,
        "tcp_flags": tcp_flags,
        "label": label,
        "source": "live-stream",
    }


def main():
    args = parse_arguments()
    logger.info("Starting ingestion stream producer in %s mode (Attack Rate: %.1f%%)...", args.mode, args.attack_rate * 100)

    # Try setting up Kafka producer
    kafka_producer = None
    try:
        from kafka import KafkaProducer
        kafka_producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=3,
        )
        logger.info("Kafka producer initialized successfully.")
    except Exception as e:
        logger.warning("Kafka client unavailable (%s). Falling back to REST POST ingestion.", e)

    count = 0
    try:
        while True:
            event = simulate_network_event(args.attack_rate)
            
            if kafka_producer:
                try:
                    kafka_producer.send("raw-logs", event)
                    logger.info("[%d] Ingested event to Kafka: %s→%s", count, event["source_ip"], event["destination_ip"])
                except Exception as k_err:
                    logger.error("Failed to push to Kafka: %s", k_err)
            else:
                # Fallback to direct HTTP POST Ingestion REST endpoint
                try:
                    r = requests.post(args.dest_url, json=event, timeout=2)
                    if r.status_code == 201:
                        logger.info("[%d] Ingested log to DB (REST): %s→%s (%s)", count, event["source_ip"], event["destination_ip"], event["label"])
                    else:
                        logger.error("REST Ingestion rejected event (HTTP %d): %s", r.status_code, r.text)
                except Exception as r_err:
                    logger.debug("REST Ingestion temporarily offline: %s", r_err)

            count += 1
            time.sleep(args.speed)

    except KeyboardInterrupt:
        logger.info("Stopping producer...")
        if kafka_producer:
            kafka_producer.close()


if __name__ == "__main__":
    main()
