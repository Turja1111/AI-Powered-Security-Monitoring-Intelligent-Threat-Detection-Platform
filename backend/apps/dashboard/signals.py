import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.alerts.models import Alert
from apps.alerts.serializers import AlertSerializer

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Alert)
def broadcast_alert_on_save(sender, instance, created, **kwargs):
    """
    Signal receiver to broadcast newly created alerts to the 'alerts' channel layer.
    """
    if created:
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                serializer = AlertSerializer(instance)
                async_to_sync(channel_layer.group_send)(
                    "alerts",
                    {
                        "type": "alert_message",
                        "data": serializer.data,
                    }
                )
                logger.info("Broadcasted alert %s to WebSocket", instance.id)
            else:
                logger.warning("Channel layer not configured — WebSocket broadcast skipped")
        except Exception as e:
            logger.exception("Failed to broadcast alert to WebSocket: %s", e)
