from django.utils import timezone
from django.conf import settings
from rest_framework import permissions
import time

from .models import Hub


class AppkeyRequired(permissions.BasePermission):
    """ Requires the user to pass a valid appkey in the request header """

    def has_permission(self, request, view):
        token = request.META.get("HTTP_X_APPKEY")
        return token is not None and token == settings.APP_KEY

class HubUuidRequired(permissions.BasePermission):
    """
    Requires a valid Hub UUID be passed in the header
    Also updates the heartbeat value for the hub that matches the UUID given
    If HTTP_X_HUB_TIME is passed in the headers, updates last_hub_time
    """

    def has_permission(self, request, view):
        hub_uuid = request.META.get("HTTP_X_HUB_UUID")
        hub_time = request.META.get("HTTP_X_HUB_TIME")
        try:
            hub = Hub.objects.get(uuid=hub_uuid)
        except Hub.DoesNotExist:
           return False

        hub.last_seen_ts = int(time.time())
        if hub_time is not None:
            hub.last_hub_time_ts = hub_time

        remote_addr = request.META.get("REMOTE_ADDR")
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded is not None:
            hub.ip_address = x_forwarded
        elif remote_addr is not None:
            hub.ip_address = remote_addr

        hub.save()

        return True


