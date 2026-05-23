"""Serializers for alert management."""
from rest_framework import serializers
from .models import Alert, ModelRegistry


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AlertUpdateSerializer(serializers.ModelSerializer):
    """For PATCH — only status, acknowledged_by, resolved_at are writable."""
    class Meta:
        model = Alert
        fields = ["status", "acknowledged_by", "resolved_at"]


class AlertSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    open = serializers.IntegerField()
    acknowledged = serializers.IntegerField()
    resolved = serializers.IntegerField()
    critical = serializers.IntegerField()
    high = serializers.IntegerField()
    medium = serializers.IntegerField()
    low = serializers.IntegerField()


class ModelRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelRegistry
        fields = "__all__"
        read_only_fields = ["id", "training_date"]
