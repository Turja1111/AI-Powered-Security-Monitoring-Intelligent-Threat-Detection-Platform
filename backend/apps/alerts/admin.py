"""Admin registration for alerts and model registry."""
from django.contrib import admin
from .models import Alert, ModelRegistry


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["created_at", "severity", "alert_type", "source_ip", "status", "anomaly_score", "confidence"]
    list_filter = ["severity", "status", "alert_type", "created_at"]
    search_fields = ["source_ip", "destination_ip", "description"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]


@admin.register(ModelRegistry)
class ModelRegistryAdmin(admin.ModelAdmin):
    list_display = ["model_name", "version", "algorithm", "f1_score", "precision_score", "recall_score", "roc_auc", "is_active", "training_date"]
    list_filter = ["is_active", "algorithm", "training_date"]
    search_fields = ["model_name", "algorithm", "mlflow_run_id"]
    date_hierarchy = "training_date"
    readonly_fields = ["training_date"]
