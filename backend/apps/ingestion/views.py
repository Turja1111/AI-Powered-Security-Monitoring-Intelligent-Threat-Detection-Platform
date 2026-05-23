"""Views for log ingestion API."""
import csv
import io
import logging
from datetime import timedelta

from django.db.models import Count, Max, Min
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BatchUploadJob, LogEntry
from .serializers import (
    BatchUploadJobSerializer,
    BatchUploadSerializer,
    LogEntryCreateSerializer,
    LogEntrySerializer,
    LogStatsSerializer,
)

logger = logging.getLogger(__name__)


from .filters import LogEntryFilter

from .kafka_producer import SecurityLogKafkaProducer

kafka_producer = SecurityLogKafkaProducer()

class LogEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for log entry CRUD operations.

    list:   GET  /api/v1/logs/
    create: POST /api/v1/logs/event/
    read:   GET  /api/v1/logs/{id}/
    """

    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [AllowAny]
    filterset_class = LogEntryFilter
    search_fields = ["source_ip", "destination_ip", "label"]
    ordering_fields = ["timestamp", "ingested_at", "bytes_sent", "duration_ms"]
    ordering = ["-timestamp"]

    def get_serializer_class(self):
        if self.action == "create":
            return LogEntryCreateSerializer
        return LogEntrySerializer

    def perform_create(self, serializer):
        """Save log entry and optionally publish to Kafka."""
        instance = serializer.save()
        logger.info("Log entry created: %s", instance.id)
        
        # Publish to Kafka
        try:
            log_data = serializer.data
            log_data["id"] = str(instance.id)
            kafka_producer.publish_log(log_data)
        except Exception as e:
            logger.error("Failed to publish log entry to Kafka: %s", e)
            
        return instance

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Aggregated log statistics endpoint."""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_logs = LogEntry.objects.count()
        logs_today = LogEntry.objects.filter(timestamp__gte=today_start).count()

        # Logs per minute (last hour)
        hour_ago = now - timedelta(hours=1)
        logs_last_hour = LogEntry.objects.filter(timestamp__gte=hour_ago).count()
        logs_per_minute = round(logs_last_hour / 60.0, 2)

        # By protocol
        by_protocol = dict(
            LogEntry.objects.values_list("protocol")
            .annotate(count=Count("id"))
            .values_list("protocol", "count")
        )

        # By label
        by_label = dict(
            LogEntry.objects.values_list("label")
            .annotate(count=Count("id"))
            .values_list("label", "count")
        )

        # Top source IPs
        top_ips = list(
            LogEntry.objects.values("source_ip")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Time range
        time_agg = LogEntry.objects.aggregate(
            earliest=Min("timestamp"), latest=Max("timestamp")
        )

        data = {
            "total_logs": total_logs,
            "logs_today": logs_today,
            "logs_per_minute": logs_per_minute,
            "by_protocol": by_protocol,
            "by_label": by_label,
            "top_source_ips": top_ips,
            "time_range": {
                "earliest": time_agg["earliest"],
                "latest": time_agg["latest"],
            },
        }
        return Response(data)


class BatchUploadView(APIView):
    """Upload CSV file with log entries for batch processing."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request):
        """Accept CSV upload and trigger async processing."""
        serializer = BatchUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        csv_file = serializer.validated_data["file"]
        source = serializer.validated_data.get("source", "csv-upload")

        # Create job record
        job = BatchUploadJob.objects.create(
            filename=csv_file.name,
            status="PROCESSING",
        )

        try:
            # Read CSV
            decoded = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))
            rows = list(reader)
            job.total_records = len(rows)
            job.save()

            # Process rows
            created = 0
            failed = 0
            for row in rows:
                try:
                    LogEntry.objects.create(
                        timestamp=row.get("timestamp", timezone.now()),
                        source_ip=row.get("source_ip", row.get("src_ip", "0.0.0.0")),
                        destination_ip=row.get("destination_ip", row.get("dst_ip", "0.0.0.0")),
                        source_port=int(row.get("source_port", row.get("src_port", 0))),
                        destination_port=int(row.get("destination_port", row.get("dst_port", 0))),
                        protocol=row.get("protocol", "TCP").upper(),
                        bytes_sent=int(row.get("bytes_sent", row.get("total_fwd_packets", 0))),
                        bytes_received=int(row.get("bytes_received", row.get("total_bwd_packets", 0))),
                        duration_ms=int(float(row.get("duration_ms", row.get("flow_duration", 0)))),
                        packet_count=int(row.get("packet_count", row.get("total_packets", 0))),
                        tcp_flags=row.get("tcp_flags", ""),
                        label=row.get("label", row.get("Label", "BENIGN")),
                        source=source,
                    )
                    created += 1
                except Exception as e:
                    failed += 1
                    logger.warning("Failed to process row: %s", e)

            job.processed_records = created
            job.failed_records = failed
            job.status = "COMPLETED"
            job.completed_at = timezone.now()
            job.save()

            return Response(
                BatchUploadJobSerializer(job).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            job.status = "FAILED"
            job.error_message = str(e)
            job.save()
            logger.exception("Batch upload failed: %s", e)
            return Response(
                {"error": str(e), "job_id": str(job.id)},
                status=status.HTTP_400_BAD_REQUEST,
            )
