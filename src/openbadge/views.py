import simplejson, pytz, StringIO
import datetime, random, math
from decimal import Decimal
from dateutil.parser import parse as parse_date

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from functools import wraps
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile

from .decorators import app_view
from .models import StudyGroup, StudyMember, Meeting

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

    log_file = request.FILES.get("file")
    meeting_uuid = request.POST.get("uuid")
    moderator_key = request.POST.get("moderator")
    members = request.POST.get("members")
    group_key = request.POST.get("group")
    start_time = parse_date(request.POST.get("startTime"))
    end_time = parse_date(request.POST.get("endTime"))
    meeting_location = request.POST.get("location")
    meeting_type = request.POST.get("type")
    meeting_description = request.POST.get("description")
    is_complete = request.POST.get("isComplete") == 'true'
    show_visualization = request.POST.get("showVisualization") == 'true'

    try:
        meeting = Meeting.objects.select_related('moderator', 'group').get(group__key=group_key, uuid=meeting_uuid)
    except Meeting.DoesNotExist:
        meeting = Meeting()
        group = StudyGroup.objects.get(key=group_key)
        meeting.group = group
        meeting.uuid = meeting_uuid

    meeting.log_file = log_file
    try:
        if moderator_key:
            meeting.moderator = StudyMember.objects.get(key=moderator_key)
        else:
            meeting.moderator = None
    except Exception, e:
        pass
    meeting.members = members
    meeting.start_time = start_time
    meeting.type = meeting_type
    meeting.location = meeting_location
    meeting.description = meeting_description
    meeting.end_time = end_time
    meeting.is_complete = is_complete
    meeting.show_visualization = show_visualization
    meeting.save()



    return json_response(success=True)


@app_view
@api_view(['GET'])
def get_group(request, group_key):

    if not group_key:
        raise Http404()

    try:
        group = StudyGroup.objects.prefetch_related("members", "visualization_ranges").get(key=group_key)
    except StudyGroup.DoesNotExist:
        raise Http404()

    return json_response(success=True, group=group.to_dict())
