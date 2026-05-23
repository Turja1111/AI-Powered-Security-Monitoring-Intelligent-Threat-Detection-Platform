"""URL routing for alerts and model registry."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlertViewSet, ModelRegistryViewSet

router = DefaultRouter()
router.register(r"alerts", AlertViewSet, basename="alerts")
router.register(r"models", ModelRegistryViewSet, basename="models")

urlpatterns = [
    path("", include(router.urls)),
]
