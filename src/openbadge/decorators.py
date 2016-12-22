from functools import wraps
import time

from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from .models import Hub


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


def is_own_project(f):
    """
    Ensures a hub that accesses a given /:projectID/whatever
    is a member of the project with that ID, **OR GOD**

    Requires a valid hub uuid to be passed in the request header

    Updates the hub's heartbeat field
    """

    @wraps(f)
    def wrap(request, project_key, *args, **kwargs):
        god_key = request.META.get("HTTP_X_GODKEY")
        if god_key == settings.GOD_KEY:
            return f(request, project_key, *args, **kwargs)


        hub_uuid = request.META.get("HTTP_X_HUB_UUID")
        try:
            hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
        except Hub.DoesNotExist:
            return HttpResponseNotFound()

        hub.last_seen_ts = int(time.time())
        hub.save()

        hub_project_key = hub.project.key
        if str(hub_project_key) == str(project_key):
            return f(request, project_key, *args, **kwargs)

        return HttpResponseUnauthorized()

    return wrap


def app_view(f):
    """ensures a valid X-APPKEY has been set in a request's header"""

    @wraps(f)
    def wrap(request, *args, **kwargs):
        token = request.META.get("HTTP_X_APPKEY")
        if token != settings.APP_KEY:
            return HttpResponseBadRequest()

        return f(request, *args, **kwargs)

    return wrap


def is_god(f):
    """ensures a valid X-GODKEY has been set in the request's header"""

    @wraps(f)
    def wrap(request, *args, **kwargs):
        god_key = request.META.get("HTTP_X_GODKEY")
        if god_key != settings.GOD_KEY:
            return HttpResponseForbidden()

        return f(request, *args, **kwargs)

    return wrap
