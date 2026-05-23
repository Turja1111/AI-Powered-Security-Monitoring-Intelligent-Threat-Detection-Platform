import pytest
from django.utils import timezone
from apps.ingestion.models import LogEntry
from apps.pipeline.feature_engineering import extract_features, FEATURE_NAMES

@pytest.mark.django_db
def test_feature_extraction_empty():
    # If no logs exist, extract_features should return 0.0 for all features
    window_end = timezone.now()
    window_start = window_end - timezone.timedelta(minutes=5)
    
    logs_qs = LogEntry.objects.all()
    features = extract_features(logs_qs, window_start, window_end, "192.168.1.100")
    
    assert len(features) == len(FEATURE_NAMES)
    assert all(v == 0.0 for v in features.values())

@pytest.mark.django_db
def test_feature_extraction_with_logs():
    window_end = timezone.now()
    window_start = window_end - timezone.timedelta(minutes=5)
    source_ip = "192.168.1.105"
    
    # Create sample logs for feature calculation
    LogEntry.objects.create(
        timestamp=window_end - timezone.timedelta(minutes=2),
        source_ip=source_ip,
        destination_ip="10.0.0.1",
        source_port=1234,
        destination_port=80,
        protocol="TCP",
        bytes_sent=1000,
        bytes_received=2000,
        duration_ms=500,
        packet_count=10,
        tcp_flags="SYN",
        label="BENIGN",
        source="live"
    )
    
    LogEntry.objects.create(
        timestamp=window_end - timezone.timedelta(minutes=1),
        source_ip=source_ip,
        destination_ip="10.0.0.1",
        source_port=1235,
        destination_port=80,
        protocol="TCP",
        bytes_sent=500,
        bytes_received=500,
        duration_ms=200,
        packet_count=5,
        tcp_flags="SYN ACK",
        label="BENIGN",
        source="live"
    )

    logs_qs = LogEntry.objects.all()
    features = extract_features(logs_qs, window_start, window_end, source_ip)
    
    assert features["connection_count"] == 2.0
    assert features["total_bytes_sent"] == 1500.0
    assert features["total_bytes_received"] == 2500.0
    assert features["total_packets"] == 15.0
    assert features["unique_dest_ips"] == 1.0
    assert features["tcp_ratio"] == 1.0
