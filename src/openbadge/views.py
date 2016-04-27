import simplejson, pytz, StringIO
import datetime, random, math
from decimal import Decimal

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from functools import wraps
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile

from .decorators import app_view
from .models import StudyGroup, StudyMember

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def json_response(**kwargs):
    return HttpResponse(simplejson.dumps(kwargs))

def context(**extra):
    return dict(**extra)

@app_view
def test(request):
    return json_response(success=True)


def test_error(request):
    raise simplejson.JSONDecodeError
    return HttpResponse()


def render_to(template):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            out = func(request, *args, **kwargs)
            if isinstance(out, dict):
                out = render(request, template, out)
            return out
        return wrapper
    return decorator


@app_view
@api_view(['POST'])
def log_data(request):

    return json_response(success=True)


@app_view
@api_view(['GET'])
def get_group(request, group_key):

    if not group_key:
        raise Http404()

    try:
        group = StudyGroup.objects.prefetch_related("members").get(key=group_key)
    except StudyGroup.DoesNotExist:
        raise Http404()

    return json_response(success=True, group=group.to_dict())
