from django.urls import re_path

from .consumers import SecurityAlertsConsumer

websocket_urlpatterns = [
    re_path(r"ws/alerts/$", SecurityAlertsConsumer.as_asgi()),
]
