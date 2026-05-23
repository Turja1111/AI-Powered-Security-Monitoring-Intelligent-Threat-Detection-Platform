"""URL routing for ingestion app."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BatchUploadView, LogEntryViewSet

router = DefaultRouter()
router.register(r"logs", LogEntryViewSet, basename="logs")

urlpatterns = [
    path("logs/batch/", BatchUploadView.as_view(), name="batch-upload"),
    path("", include(router.urls)),
]
