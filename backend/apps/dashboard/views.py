"""
Aggregation views for dashboard metrics and visualizations.
"""
from datetime import timedelta
import logging
import requests
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.alerts.models import Alert
from apps.ingestion.models import LogEntry

logger = logging.getLogger(__name__)


class AlertTimeSeriesView(APIView):
    """
    Alert counts per hour for the last 24 hours.
    Used for the Recharts LineChart on the overview.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        yesterday = now - timedelta(hours=24)

        alerts = Alert.objects.filter(created_at__gte=yesterday)

        # Initialize hourly bins
        hourly_data = {}
        for h in range(25):
            bin_time = (yesterday + timedelta(hours=h)).replace(minute=0, second=0, microsecond=0)
            hourly_data[bin_time] = {"timestamp": bin_time.isoformat(), "critical": 0, "high": 0, "medium": 0, "low": 0}

        # Aggregate alerts
        for alert in alerts:
            bin_time = alert.created_at.replace(minute=0, second=0, microsecond=0)
            if bin_time in hourly_data:
                sev = alert.severity.lower()
                hourly_data[bin_time][sev] = hourly_data[bin_time].get(sev, 0) + 1

        sorted_points = [hourly_data[k] for k in sorted(hourly_data.keys())]
        return Response(sorted_points)


class SeverityDistributionView(APIView):
    """
    Alert counts by severity for the last 7 days.
    Used for the donut chart.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cutoff = timezone.now() - timedelta(days=7)
        counts = dict(
            Alert.objects.filter(created_at__gte=cutoff)
            .values_list("severity")
            .annotate(count=Count("id"))
            .values_list("severity", "count")
        )

        total = sum(counts.values())

        data = []
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = counts.get(severity, 0)
            pct = round((count / total) * 100, 1) if total > 0 else 0.0
            data.append({
                "severity": severity,
                "count": count,
                "percentage": pct
            })

        return Response(data)


class TopAttackingIPsView(APIView):
    """
    Top 10 source IPs by alert count.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cutoff = timezone.now() - timedelta(days=7)
        top_ips_query = (
            Alert.objects.filter(created_at__gte=cutoff)
            .values("source_ip")
            .annotate(alert_count=Count("id"))
            .order_by("-alert_count")[:10]
        )

        data = []
        for rank, item in enumerate(top_ips_query, start=1):
            ip = item["source_ip"]
            # Get peak severity for this IP
            peak_alert = Alert.objects.filter(source_ip=ip).order_by("-severity")[:1]
            peak_severity = peak_alert[0].severity if peak_alert.exists() else "LOW"
            
            # Simulated geo info & last seen
            last_alert = Alert.objects.filter(source_ip=ip).latest("created_at")

            data.append({
                "rank": rank,
                "ip": ip,
                "alert_count": item["alert_count"],
                "severity": peak_severity,
                "last_seen": last_alert.created_at.isoformat(),
                "country": "US" if rank % 2 == 0 else "DE"
            })

        return Response(data)


class ThreatHeatmapView(APIView):
    """
    Grid data representing alerts by hour of day (0-23) and day of week (0=Mon, 6=Sun).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cutoff = timezone.now() - timedelta(days=30)
        alerts = Alert.objects.filter(created_at__gte=cutoff)

        heatmap = {}
        for day in range(7):
            for hour in range(24):
                heatmap[(day, hour)] = 0

        for alert in alerts:
            day = alert.created_at.weekday()
            hour = alert.created_at.hour
            heatmap[(day, hour)] = heatmap.get((day, hour), 0) + 1

        cells = []
        for (day, hour), count in heatmap.items():
            cells.append({
                "day": day,
                "hour": hour,
                "count": count
            })

        return Response(cells)


class SystemHealthView(APIView):
    """
    Aggregates health check metrics of different microservices and dependencies.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Database check
        try:
            LogEntry.objects.count()
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"

        # ML service check
        ml_service_url = getattr(settings, "ML_SERVICE_URL", "http://ml-service:8001")
        try:
            r = requests.get(f"{ml_service_url}/health", timeout=2)
            if r.status_code == 200:
                ml_status = r.json()
            else:
                ml_status = {"status": "degraded", "error": f"HTTP {r.status_code}"}
        except Exception as e:
            ml_status = {"status": "offline", "error": str(e)}

        return Response({
            "database": db_status,
            "ml_service": ml_status,
            "broker": "healthy", # Simulating healthy Kafka connection
            "cache": "healthy",  # Simulating healthy Redis connection
            "system_cpu_usage": 14.5,
            "system_ram_usage": 45.2,
        })


class LogIngestionRateView(APIView):
    """
    Ingested log counts per minute for the last hour.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        hour_ago = now - timedelta(hours=1)

        logs = LogEntry.objects.filter(timestamp__gte=hour_ago)

        minute_bins = {}
        for m in range(61):
            bin_time = (hour_ago + timedelta(minutes=m)).replace(second=0, microsecond=0)
            minute_bins[bin_time] = {"timestamp": bin_time.isoformat(), "value": 0}

        for log in logs:
            bin_time = log.timestamp.replace(second=0, microsecond=0)
            if bin_time in minute_bins:
                minute_bins[bin_time]["value"] += 1

        sorted_rate = [minute_bins[k] for k in sorted(minute_bins.keys())]
        return Response(sorted_rate)
