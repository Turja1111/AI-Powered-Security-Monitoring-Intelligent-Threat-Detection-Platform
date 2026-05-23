"""
Log ingestion models — raw network event storage.
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class LogEntry(models.Model):
    """Raw ingested network log event."""

    PROTOCOL_CHOICES = [
        ("TCP", "TCP"),
        ("UDP", "UDP"),
        ("ICMP", "ICMP"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(db_index=True)
    source_ip = models.GenericIPAddressField(db_index=True)
    destination_ip = models.GenericIPAddressField()
    source_port = models.IntegerField(default=0)
    destination_port = models.IntegerField(default=0)
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, default="TCP")
    bytes_sent = models.BigIntegerField(default=0)
    bytes_received = models.BigIntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    packet_count = models.IntegerField(default=0)
    tcp_flags = models.CharField(max_length=20, blank=True, default="")
    label = models.CharField(max_length=50, default="BENIGN")
    source = models.CharField(max_length=50, default="live")
    ingested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"], name="idx_logs_timestamp"),
            models.Index(fields=["source_ip", "timestamp"], name="idx_logs_srcip_ts"),
            models.Index(fields=["label"], name="idx_logs_label"),
            models.Index(fields=["protocol"], name="idx_logs_protocol"),
        ]

    def __str__(self):
        return f"[{self.timestamp}] {self.source_ip}→{self.destination_ip} ({self.protocol})"


class BatchUploadJob(models.Model):
    """Tracks CSV batch upload jobs."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "batch_upload_jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Batch {self.id} — {self.filename} ({self.status})"
