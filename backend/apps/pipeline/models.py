"""
FeatureVector and PipelineRun models.
"""
import uuid

from django.db import models


class FeatureVector(models.Model):
    """Engineered feature vector per source IP per time window."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    window_start = models.DateTimeField(db_index=True)
    window_end = models.DateTimeField(db_index=True)
    source_ip = models.GenericIPAddressField(db_index=True)
    feature_vector = models.JSONField(help_text="Normalized features mapping")
    anomaly_score = models.FloatField(default=0.0, db_index=True)
    predicted_label = models.CharField(max_length=50, default="BENIGN", db_index=True)
    confidence = models.FloatField(default=0.0)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "features"
        ordering = ["-window_end"]
        indexes = [
            models.Index(fields=["window_start", "window_end"], name="idx_features_window"),
            models.Index(fields=["source_ip", "window_end"], name="idx_features_src_window"),
        ]

    def __str__(self):
        return f"Feature Vector for {self.source_ip} ending {self.window_end} — Anomaly: {self.anomaly_score:.3f}"


class PipelineRun(models.Model):
    """Audit trail for ETL and feature processing jobs."""

    STATUS_CHOICES = [
        ("STARTED", "Started"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="STARTED")
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "pipeline_runs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Pipeline Run {self.id} — Status: {self.status} (Processed: {self.records_processed})"
