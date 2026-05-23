"""Admin registration for pipeline models."""
from django.contrib import admin
from .models import FeatureVector, PipelineRun


@admin.register(FeatureVector)
class FeatureVectorAdmin(admin.ModelAdmin):
    list_display = ["window_end", "source_ip", "predicted_label", "confidence", "anomaly_score", "computed_at"]
    list_filter = ["predicted_label", "window_end"]
    search_fields = ["source_ip"]
    readonly_fields = ["computed_at"]


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ["started_at", "completed_at", "records_processed", "records_failed", "status"]
    list_filter = ["status", "started_at"]
    readonly_fields = ["started_at"]
