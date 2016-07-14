from functools import wraps
# from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseUnauthorized, HttpResponseNotFound
from .models import Hub


def is_own_project(f):
    """ensures a hub that accesses a given /:projectID/whatever is a member of the project with that ID, **OR GOD**"""

    @wraps(f)
    def wrap(request, project_id, *args, **kwargs):
        hub_uuid = request.META.get("HTTP_X_HUB_UUID")
        try:
            hub = Hub.objects.prefetch_related("project").get(uuid=hub_uuid)
        except Hub.DoesNotExist:
            return HttpResponseNotFound()
        hub_project_id = hub.project.id
        if str(hub_project_id) == str(project_id):
            return f(request, project_id, *args, **kwargs)

        god_key = request.META.get("HTTP_X_GODKEY")
        if god_key == settings.GOD_KEY:
            return f(request, project_id, *args, **kwargs)

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
