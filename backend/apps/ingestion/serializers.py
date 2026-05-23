"""Serializers for log ingestion endpoints."""
from rest_framework import serializers

from .models import BatchUploadJob, LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    """Full log entry serializer for CRUD operations."""

    class Meta:
        model = LogEntry
        fields = "__all__"
        read_only_fields = ["id", "ingested_at"]


class LogEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating log entries via POST."""

    class Meta:
        model = LogEntry
        exclude = ["id", "ingested_at"]


class BatchUploadSerializer(serializers.Serializer):
    """Serializer for CSV batch upload."""

    file = serializers.FileField(help_text="CSV file containing log entries")
    source = serializers.CharField(
        max_length=50, default="csv-upload", help_text="Data source label"
    )


class BatchUploadJobSerializer(serializers.ModelSerializer):
    """Serializer for batch upload job status."""

    class Meta:
        model = BatchUploadJob
        fields = "__all__"


class LogStatsSerializer(serializers.Serializer):
    """Serializer for aggregated log statistics."""

    total_logs = serializers.IntegerField()
    logs_today = serializers.IntegerField()
    logs_per_minute = serializers.FloatField()
    by_protocol = serializers.DictField(child=serializers.IntegerField())
    by_label = serializers.DictField(child=serializers.IntegerField())
    top_source_ips = serializers.ListField(child=serializers.DictField())
    time_range = serializers.DictField()
