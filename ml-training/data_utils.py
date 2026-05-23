"""
Data loading and synthetic log generation utilities for model training.
"""
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_synthetic_data(n_samples=10000, attack_ratio=0.1):
    """
    Generate realistic synthetic network logs for training.
    Modes simulated: BENIGN, PortScan, DDoS, BruteForce, Exfiltration.
    """
    np.random.seed(42)
    random.seed(42)

    records = []
    base_time = datetime.now() - timedelta(days=2)

    # Pre-generate some IPs
    benign_ips = [f"192.168.1.{i}" for i in range(10, 100)]
    attacker_ips = ["10.0.0.1", "10.0.0.2", "172.16.0.5", "172.16.0.6"]
    server_ips = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]

    n_attacks = int(n_samples * attack_ratio)
    n_benign = n_samples - n_attacks

    # Generate BENIGN records
    for i in range(n_benign):
        timestamp = base_time + timedelta(seconds=random.randint(0, 172800))
        src_ip = random.choice(benign_ips)
        dst_ip = random.choice(server_ips)
        protocol = random.choice(["TCP", "UDP", "ICMP"])
        
        if protocol == "ICMP":
            src_port = 0
            dst_port = 0
            bytes_sent = 64
            bytes_received = 64
            duration = 1
            packets = 1
        elif protocol == "UDP":
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([53, 123, 161]) # DNS, NTP, SNMP
            bytes_sent = random.randint(50, 500)
            bytes_received = random.randint(50, 1000)
            duration = random.randint(5, 100)
            packets = random.randint(2, 10)
        else:
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([80, 443, 8080]) # Web traffic
            bytes_sent = random.randint(500, 50000)
            bytes_received = random.randint(1000, 500000)
            duration = random.randint(50, 5000)
            packets = random.randint(10, 100)

        records.append({
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
            "tcp_flags": "A" if protocol == "TCP" else "",
            "label": "BENIGN",
            "source": "synthetic",
        })

    # Generate attacks (PortScan, DDoS, BruteForce, Exfiltration)
    attack_types = ["PortScan", "DDoS", "BruteForce", "Exfiltration"]

    for i in range(n_attacks):
        timestamp = base_time + timedelta(seconds=random.randint(0, 172800))
        src_ip = random.choice(attacker_ips)
        dst_ip = random.choice(server_ips)
        attack_type = random.choice(attack_types)

        if attack_type == "PortScan":
            protocol = "TCP"
            src_port = random.randint(40000, 60000)
            dst_port = random.randint(1, 1024) # Scanning low ports
            bytes_sent = 40
            bytes_received = 0
            duration = 10
            packets = 1
            tcp_flags = "S" # SYN request only
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
            dst_port = random.choice([22, 3389]) # SSH or RDP
            bytes_sent = random.randint(300, 800)
            bytes_received = random.randint(300, 600)
            duration = random.randint(100, 1000)
            packets = random.randint(5, 12)
            tcp_flags = "PA"
        else: # Exfiltration
            protocol = "TCP"
            src_port = random.randint(50000, 60000)
            dst_port = 443
            bytes_sent = random.randint(10000000, 100000000) # massive data transfer out
            bytes_received = random.randint(10000, 50000)
            duration = random.randint(60000, 300000) # long connection
            packets = random.randint(5000, 20000)
            tcp_flags = "A"

        records.append({
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
            "label": attack_type,
            "source": "synthetic",
        })

    df = pd.DataFrame(records)
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    return df


def normalize_label(label):
    """Ensure standard attack names."""
    lbl = str(label).strip()
    if lbl.upper() in ["BENIGN", "NORMAL"]:
        return "BENIGN"
    return lbl


def train_test_split_time(df, test_size=0.2):
    """Split data chronologically (time-aware split)."""
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    split_idx = int(len(df) * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]


def extract_features_df(df):
    """
    Simulate the 26 feature extraction metrics directly on a Pandas DataFrame.
    Returns: X (numpy array of shape (N, 26)) and y (labels array).
    """
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

    # Group by source_ip and hourly windows
    df = df.copy()
    df["hour"] = df["timestamp"].dt.floor("h")

    grouped = df.groupby(["source_ip", "hour"])
    X_list = []
    y_list = []

    for (src_ip, hour), group in grouped:
        count = len(group)
        if count == 0:
            continue

        total_bytes_sent = group["bytes_sent"].sum()
        total_bytes_received = group["bytes_received"].sum()
        total_packets = group["packet_count"].sum()
        avg_packet_size = (total_bytes_sent + total_bytes_received) / total_packets if total_packets > 0 else 0.0

        unique_dest_ips = group["destination_ip"].nunique()
        dest_ports = group["destination_port"].tolist()
        unique_dest_ports = len(set(dest_ports))

        tcp_count = sum(1 for p in group["protocol"] if str(p).upper() == "TCP")
        udp_count = sum(1 for p in group["protocol"] if str(p).upper() == "UDP")
        icmp_count = sum(1 for p in group["protocol"] if str(p).upper() == "ICMP")

        tcp_ratio = tcp_count / count
        udp_ratio = udp_count / count
        icmp_ratio = icmp_count / count

        # Shannon Entropy for ports
        if dest_ports:
            probs = pd.Series(dest_ports).value_counts() / len(dest_ports)
            port_entropy = -sum(probs * np.log2(probs))
        else:
            port_entropy = 0.0

        avg_duration_ms = group["duration_ms"].mean()
        bytes_per_packet = (total_bytes_sent + total_bytes_received) / total_packets if total_packets > 0 else 0.0

        connections_per_sec = count / 3600.0 # hourly buckets

        inter_arrival_mean = 0.0
        inter_arrival_std = 0.0
        if len(group) > 1:
            times = sorted(group["timestamp"])
            diffs = [(times[j] - times[j-1]).total_seconds() for j in range(1, len(times))]
            inter_arrival_mean = np.mean(diffs)
            inter_arrival_std = np.std(diffs)

        night_time_flag = 1.0 if hour.hour < 6 else 0.0
        byte_asymmetry_ratio = total_bytes_sent / (total_bytes_received + 1)

        # TCP Flags
        syn_count = sum(1 for f in group["tcp_flags"] if "S" in str(f).upper())
        ack_count = sum(1 for f in group["tcp_flags"] if "A" in str(f).upper())
        fin_count = sum(1 for f in group["tcp_flags"] if "F" in str(f).upper())
        rst_count = sum(1 for f in group["tcp_flags"] if "R" in str(f).upper())
        psh_count = sum(1 for f in group["tcp_flags"] if "P" in str(f).upper())
        urg_count = sum(1 for f in group["tcp_flags"] if "U" in str(f).upper())

        syn_flag_ratio = syn_count / count
        ack_flag_ratio = ack_count / count
        fin_flag_ratio = fin_count / count
        rst_flag_ratio = rst_count / count
        psh_flag_ratio = psh_count / count
        urg_flag_ratio = urg_count / count

        failed_connections = sum(1 for f in group["tcp_flags"] if ("S" in str(f).upper() and "A" not in str(f).upper()) or "R" in str(f).upper())
        failed_connection_ratio = failed_connections / count

        dns_queries = sum(1 for p in group["destination_port"] if p == 53)
        dns_query_ratio = dns_queries / count

        feature_vector = [
            float(total_bytes_sent),
            float(total_bytes_received),
            float(total_packets),
            float(avg_packet_size),
            float(count),
            float(unique_dest_ips),
            float(unique_dest_ports),
            float(tcp_ratio),
            float(udp_ratio),
            float(icmp_ratio),
            float(port_entropy),
            float(avg_duration_ms),
            float(bytes_per_packet),
            float(connections_per_sec),
            float(inter_arrival_mean),
            float(inter_arrival_std),
            float(night_time_flag),
            float(byte_asymmetry_ratio),
            float(failed_connection_ratio),
            float(syn_flag_ratio),
            float(ack_flag_ratio),
            float(fin_flag_ratio),
            float(rst_flag_ratio),
            float(psh_flag_ratio),
            float(urg_flag_ratio),
            float(dns_query_ratio),
        ]

        # Majority label in window is selected as window label
        label = group["label"].mode()[0] if not group["label"].empty else "BENIGN"

        X_list.append(feature_vector)
        y_list.append(label)

    return np.array(X_list), np.array(y_list)

