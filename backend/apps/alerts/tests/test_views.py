import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.alerts.models import Alert, ModelRegistry

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_alert():
    return Alert.objects.create(
        severity="HIGH",
        alert_type="ddos",
        source_ip="192.168.1.100",
        destination_ip="10.0.0.5",
        anomaly_score=0.92,
        confidence=0.95,
        predicted_label="DDoS",
        description="Simulated DDoS attack warning",
        status="OPEN"
    )

@pytest.fixture
def sample_model_registry():
    return ModelRegistry.objects.create(
        model_name="xgboost_classifier",
        version="1.0.0",
        algorithm="XGBoost",
        dataset_trained_on="CICIDS2017",
        f1_score=0.985,
        precision_score=0.988,
        recall_score=0.982,
        roc_auc=0.998,
        is_active=True
    )

@pytest.mark.django_db
class TestAlertViewSet:
    
    def test_list_alerts(self, api_client, sample_alert):
        url = reverse("alert-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1
        assert results[0]["source_ip"] == sample_alert.source_ip

    def test_filter_alerts_by_severity(self, api_client, sample_alert):
        url = reverse("alert-list")
        response = api_client.get(url, {"severity": "HIGH"})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1
        assert all(a["severity"] == "HIGH" for a in results)

    def test_acknowledge_alert(self, api_client, sample_alert):
        url = reverse("alert-detail", kwargs={"pk": sample_alert.pk})
        data = {"status": "ACKNOWLEDGED", "acknowledged_by": "sec_operator_1"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ACKNOWLEDGED"
        assert response.data["acknowledged_by"] == "sec_operator_1"
        assert Alert.objects.get(pk=sample_alert.pk).status == "ACKNOWLEDGED"

    def test_resolve_alert(self, api_client, sample_alert):
        url = reverse("alert-detail", kwargs={"pk": sample_alert.pk})
        data = {"status": "RESOLVED"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "RESOLVED"
        assert Alert.objects.get(pk=sample_alert.pk).status == "RESOLVED"

    def test_alerts_summary(self, api_client, sample_alert):
        url = reverse("alert-list") + "summary/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "OPEN" in response.data or "total_alerts" in response.data or "critical_alerts" in response.data or "severity_distribution" in response.data

@pytest.mark.django_db
class TestModelRegistryViewSet:
    
    def test_list_models(self, api_client, sample_model_registry):
        url = reverse("modelregistry-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1
        assert results[0]["model_name"] == sample_model_registry.model_name
        assert results[0]["is_active"] is True
