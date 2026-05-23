"""Admin registration for ingestion models."""
from django.contrib import admin
from .models import LogEntry, BatchUploadJob


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "source_ip", "destination_ip", "protocol", "label", "source"]
    list_filter = ["protocol", "label", "source"]
    search_fields = ["source_ip", "destination_ip"]
    readonly_fields = ["id", "ingested_at"]
    date_hierarchy = "timestamp"


@admin.register(BatchUploadJob)
class BatchUploadJobAdmin(admin.ModelAdmin):
    list_display = ["id", "filename", "status", "total_records", "processed_records", "created_at"]
    list_filter = ["status"]
    readonly_fields = ["id", "created_at", "completed_at"]
