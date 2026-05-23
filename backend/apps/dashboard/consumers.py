import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from apps.alerts.models import Alert
from apps.alerts.serializers import AlertSerializer

logger = logging.getLogger(__name__)


class SecurityAlertsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming real-time security alerts.
    """

    async def connect(self):
        self.group_name = "alerts"

        # Join alerts group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info("WebSocket connected: %s", self.channel_name)

        # Send last 20 open/recent alerts upon connection
        recent_alerts = await self.get_recent_alerts()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "initial_alerts",
                    "data": recent_alerts,
                }
            )
        )

    async def disconnect(self, close_code):
        # Leave alerts group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WebSocket disconnected: %s with code %s", self.channel_name, close_code)

    async def receive(self, text_data):
        """Receive action from WebSocket client (e.g. ping)."""
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except Exception as e:
            logger.error("WebSocket receive error: %s", e)

    async def alert_message(self, event):
        """Broadcast alert message to WebSocket client."""
        alert_data = event["data"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_alert",
                    "data": alert_data,
                }
            )
        )

    @database_sync_to_async
    def get_recent_alerts(self):
        """Fetch last 20 alerts to bootstrap the UI feed."""
        alerts = Alert.objects.all()[:20]
        # We can serialize them with AlertSerializer
        # We need to pass many=True and .data
        # Note: serializing in DB context or outside
        serializer = AlertSerializer(alerts, many=True)
        return serializer.data
