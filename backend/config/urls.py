"""
URL Configuration for AI Security Monitoring Platform.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# ── Health check ──────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Basic health check endpoint."""
    return Response({"status": "healthy", "service": "django-backend", "version": "1.0.0"})


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check
    path("api/v1/health/", health_check, name="health-check"),

    # App APIs
    path("api/v1/", include("apps.ingestion.urls")),
    path("api/v1/", include("apps.alerts.urls")),
    path("api/v1/", include("apps.dashboard.urls")),

    # OpenAPI docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
