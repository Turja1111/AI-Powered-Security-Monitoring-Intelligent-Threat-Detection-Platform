from django.urls import path

from .views import (
    AlertTimeSeriesView,
    SeverityDistributionView,
    TopAttackingIPsView,
    ThreatHeatmapView,
    SystemHealthView,
    LogIngestionRateView,
)

urlpatterns = [
    path("alerts/timeseries/", AlertTimeSeriesView.as_view(), name="alerts-timeseries"),
    path("alerts/severity/", SeverityDistributionView.as_view(), name="alerts-severity"),
    path("alerts/top-ips/", TopAttackingIPsView.as_view(), name="alerts-top-ips"),
    path("threats/heatmap/", ThreatHeatmapView.as_view(), name="threats-heatmap"),
    path("system/health/", SystemHealthView.as_view(), name="system-health"),
    path("logs/rate/", LogIngestionRateView.as_view(), name="logs-ingestion-rate"),
]
