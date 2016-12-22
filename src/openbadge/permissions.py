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
    """

    def has_permission(self, request, view):
        hub_uuid = request.META.get("HTTP_X_HUB_UUID")
        try:        
            hub = Hub.objects.get(uuid=hub_uuid)
        except Hub.DoesNotExist:
           return False 
        
        hub.last_seen_ts = int(time.time())
        hub.save()
        return True
