"""Views for alert management and model registry API."""
import logging
from django.utils import timezone
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Alert, ModelRegistry
from .serializers import (
    AlertSerializer,
    AlertUpdateSerializer,
    AlertSummarySerializer,
    ModelRegistrySerializer,
)

logger = logging.getLogger(__name__)


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Alert operations.
    Supports list, retrieve, and partial_update.
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["severity", "status", "alert_type", "source_ip", "destination_ip"]
    search_fields = ["source_ip", "destination_ip", "description", "alert_type"]
    ordering_fields = ["created_at", "anomaly_score", "confidence"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["partial_update", "update"]:
            return AlertUpdateSerializer
        return AlertSerializer

    def perform_update(self, serializer):
        """Handle updating the alert status and timestamps."""
        new_status = serializer.validated_data.get("status")
        instance = self.get_object()

        if new_status == "RESOLVED" and instance.status != "RESOLVED":
            serializer.save(resolved_at=timezone.now())
        else:
            serializer.save()

        logger.info("Alert %s updated to status %s", instance.id, new_status)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """Return counts of alerts grouped by status and severity."""
        total = Alert.objects.count()
        open_count = Alert.objects.filter(status="OPEN").count()
        ack_count = Alert.objects.filter(status="ACKNOWLEDGED").count()
        res_count = Alert.objects.filter(status="RESOLVED").count()

        sev_counts = dict(
            Alert.objects.values_list("severity")
            .annotate(count=Count("id"))
            .values_list("severity", "count")
        )

        data = {
            "total": total,
            "open": open_count,
            "acknowledged": ack_count,
            "resolved": res_count,
            "critical": sev_counts.get("CRITICAL", 0),
            "high": sev_counts.get("HIGH", 0),
            "medium": sev_counts.get("MEDIUM", 0),
            "low": sev_counts.get("LOW", 0),
        }

        serializer = AlertSummarySerializer(data)
        return Response(serializer.data)


class ModelRegistryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ModelRegistry management.
    """
    queryset = ModelRegistry.objects.all()
    serializer_class = ModelRegistrySerializer
    permission_classes = [AllowAny]
    filterset_fields = ["model_name", "is_active", "algorithm"]
    search_fields = ["model_name", "algorithm", "mlflow_run_id"]
    ordering_fields = ["training_date", "f1_score", "precision_score", "recall_score", "roc_auc"]
    ordering = ["-training_date"]

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """Activate this model version and deactivate other versions of the same model."""
        model_version = self.get_object()
        
        # Deactivate all other versions of the same model
        ModelRegistry.objects.filter(model_name=model_version.model_name).exclude(pk=model_version.pk).update(is_active=False)
        
        model_version.is_active = True
        model_version.save()
        
        logger.info("Model %s v%s activated", model_version.model_name, model_version.version)
        return Response(self.get_serializer(model_version).data)
