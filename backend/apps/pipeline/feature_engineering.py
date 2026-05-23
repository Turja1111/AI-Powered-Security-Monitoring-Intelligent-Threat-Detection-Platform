"""
Feature Engineering engine for extracting normalized network metrics from log data.
"""
import math
from datetime import datetime, time
import numpy as np
import pandas as pd
from django.db.models import Count, Sum, Avg, StdDev
from django.utils import timezone


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


def calculate_entropy(values):
    """Calculate Shannon Entropy for a list of values."""
    if not values:
        return 0.0
    counts = pd.Series(values).value_counts()
    probs = counts / len(values)
    return -sum(probs * np.log2(probs))


def extract_features(logs_queryset, window_start, window_end, source_ip):
    """
    Extract a dictionary of 26 features from a queryset of LogEntry records.
    Features are aggregated for a specific source IP within a time window.
    """
    logs = list(logs_queryset.filter(source_ip=source_ip, timestamp__range=(window_start, window_end)))
    count = len(logs)

    if count == 0:
        return {name: 0.0 for name in FEATURE_NAMES}

    # Volume Calculations
    total_bytes_sent = sum(log.bytes_sent for log in logs)
    total_bytes_received = sum(log.bytes_received for log in logs)
    total_packets = sum(log.packet_count for log in logs)
    avg_packet_size = (total_bytes_sent + total_bytes_received) / total_packets if total_packets > 0 else 0.0

    dest_ips = {log.destination_ip for log in logs}
    dest_ports = [log.destination_port for log in logs]
    unique_dest_ports = len(set(dest_ports))

    # Behavioural Calculations
    tcp_count = sum(1 for log in logs if log.protocol.upper() == "TCP")
    udp_count = sum(1 for log in logs if log.protocol.upper() == "UDP")
    icmp_count = sum(1 for log in logs if log.protocol.upper() == "ICMP")

    tcp_ratio = tcp_count / count
    udp_ratio = udp_count / count
    icmp_ratio = icmp_count / count

    port_entropy = calculate_entropy(dest_ports)
    avg_duration_ms = sum(log.duration_ms for log in logs) / count
    bytes_per_packet = (total_bytes_sent + total_bytes_received) / total_packets if total_packets > 0 else 0.0

    # Temporal Calculations
    duration_sec = (window_end - window_start).total_seconds()
    connections_per_sec = count / duration_sec if duration_sec > 0 else 0.0

    # Inter-arrival times
    timestamps = sorted([log.timestamp for log in logs])
    inter_arrivals = []
    for i in range(1, len(timestamps)):
        diff = (timestamps[i] - timestamps[i-1]).total_seconds()
        inter_arrivals.append(diff)

    if inter_arrivals:
        inter_arrival_mean = np.mean(inter_arrivals)
        inter_arrival_std = np.std(inter_arrivals)
    else:
        inter_arrival_mean = 0.0
        inter_arrival_std = 0.0

    # Night time flag (00:00 - 06:00 UTC)
    start_time = window_start.time()
    night_time_flag = 1.0 if start_time >= time(0, 0) and start_time <= time(6, 0) else 0.0

    # Derived Calculations
    byte_asymmetry_ratio = total_bytes_sent / (total_bytes_received + 1)
    
    # TCP Flags calculations
    syn_count = sum(1 for log in logs if "S" in log.tcp_flags.upper() or "SYN" in log.tcp_flags.upper())
    ack_count = sum(1 for log in logs if "A" in log.tcp_flags.upper() or "ACK" in log.tcp_flags.upper())
    fin_count = sum(1 for log in logs if "F" in log.tcp_flags.upper() or "FIN" in log.tcp_flags.upper())
    rst_count = sum(1 for log in logs if "R" in log.tcp_flags.upper() or "RST" in log.tcp_flags.upper())
    psh_count = sum(1 for log in logs if "P" in log.tcp_flags.upper() or "PSH" in log.tcp_flags.upper())
    urg_count = sum(1 for log in logs if "U" in log.tcp_flags.upper() or "URG" in log.tcp_flags.upper())

    syn_flag_ratio = syn_count / count
    ack_flag_ratio = ack_count / count
    fin_flag_ratio = fin_count / count
    rst_flag_ratio = rst_count / count
    psh_flag_ratio = psh_count / count
    urg_flag_ratio = urg_count / count

    # Connection failure estimation: connection with SYN but no ACK, or a high number of reset connections
    failed_connections = sum(1 for log in logs if ("S" in log.tcp_flags.upper() and "A" not in log.tcp_flags.upper()) or "R" in log.tcp_flags.upper())
    failed_connection_ratio = failed_connections / count

    dns_queries = sum(1 for log in logs if log.destination_port == 53)
    dns_query_ratio = dns_queries / count

    feature_dict = {
        "total_bytes_sent": float(total_bytes_sent),
        "total_bytes_received": float(total_bytes_received),
        "total_packets": float(total_packets),
        "avg_packet_size": float(avg_packet_size),
        "connection_count": float(count),
        "unique_dest_ips": float(len(dest_ips)),
        "unique_dest_ports": float(unique_dest_ports),
        "tcp_ratio": float(tcp_ratio),
        "udp_ratio": float(udp_ratio),
        "icmp_ratio": float(icmp_ratio),
        "port_entropy": float(port_entropy),
        "avg_duration_ms": float(avg_duration_ms),
        "bytes_per_packet": float(bytes_per_packet),
        "connections_per_sec": float(connections_per_sec),
        "inter_arrival_mean": float(inter_arrival_mean),
        "inter_arrival_std": float(inter_arrival_std),
        "night_time_flag": float(night_time_flag),
        "byte_asymmetry_ratio": float(byte_asymmetry_ratio),
        "failed_connection_ratio": float(failed_connection_ratio),
        "syn_flag_ratio": float(syn_flag_ratio),
        "ack_flag_ratio": float(ack_flag_ratio),
        "fin_flag_ratio": float(fin_flag_ratio),
        "rst_flag_ratio": float(rst_flag_ratio),
        "psh_flag_ratio": float(psh_flag_ratio),
        "urg_flag_ratio": float(urg_flag_ratio),
        "dns_query_ratio": float(dns_query_ratio),
    }

    return feature_dict


def get_feature_list(feature_dict):
    """Convert features dictionary to standard ordered float list."""
    return [feature_dict[name] for name in FEATURE_NAMES]
