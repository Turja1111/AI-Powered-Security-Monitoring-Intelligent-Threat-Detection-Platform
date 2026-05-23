import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.ingestion.models import LogEntry, BatchUploadJob

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_log_entry():
    return LogEntry.objects.create(
        timestamp=timezone.now(),
        source_ip="192.168.1.50",
        destination_ip="10.0.0.1",
        source_port=1234,
        destination_port=80,
        protocol="TCP",
        bytes_sent=500,
        bytes_received=1000,
        duration_ms=100,
        packet_count=10,
        tcp_flags="SYN",
        label="BENIGN",
        source="live"
    )

@pytest.mark.django_db
class TestLogEntryViewSet:
    
    def test_list_logs(self, api_client, sample_log_entry):
        url = reverse("logentry-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Check if sample log entry is in response (rest_framework pagination returns 'results')
        results = response.data.get("results", response.data)
        assert len(results) >= 1
        assert results[0]["source_ip"] == sample_log_entry.source_ip

    def test_create_log_event(self, api_client):
        url = reverse("logentry-list") + "event/"
        data = {
            "timestamp": timezone.now().isoformat(),
            "source_ip": "172.16.0.4",
            "destination_ip": "10.0.0.1",
            "source_port": 5432,
            "destination_port": 80,
            "protocol": "TCP",
            "bytes_sent": 100,
            "bytes_received": 200,
            "duration_ms": 50,
            "packet_count": 5,
            "tcp_flags": "ACK",
            "label": "BENIGN",
            "source": "live"
        }
        # In LogEntryViewSet, perform_create would attempt to push to Kafka, which we mock/ignore
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert LogEntry.objects.filter(source_ip="172.16.0.4").exists()

    def test_get_log_detail(self, api_client, sample_log_entry):
        url = reverse("logentry-detail", kwargs={"pk": sample_log_entry.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["source_ip"] == sample_log_entry.source_ip

    def test_get_stats(self, api_client, sample_log_entry):
        url = reverse("logentry-list") + "stats/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "total_logs" in response.data
        assert "logs_today" in response.data
        assert response.data["total_logs"] >= 1

@pytest.mark.django_db
class TestBatchUploadView:
    
    def test_upload_invalid_csv(self, api_client):
        url = reverse("batch-upload")
        # Send empty file or non-CSV data
        response = api_client.post(url, {"file": "not a file"}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_valid_csv(self, api_client):
        url = reverse("batch-upload")
        
        # Create an in-memory CSV file
        csv_content = (
            "timestamp,source_ip,destination_ip,source_port,destination_port,protocol,bytes_sent,bytes_received,duration_ms,packet_count,tcp_flags,label\n"
            f"{timezone.now().isoformat()},192.168.1.10,10.0.0.2,4321,80,TCP,150,300,20,4,SYN,BENIGN\n"
            f"{timezone.now().isoformat()},192.168.1.11,10.0.0.3,4322,443,TCP,250,500,40,8,SYN,PortScan\n"
        )
        
        from io import BytesIO
        csv_file = BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test_logs.csv'
        
        response = api_client.post(url, {"file": csv_file, "source": "test-upload"}, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "COMPLETED"
        assert response.data["total_records"] == 2
        assert LogEntry.objects.filter(source_ip="192.168.1.10").exists()
        assert LogEntry.objects.filter(source_ip="192.168.1.11").exists()
