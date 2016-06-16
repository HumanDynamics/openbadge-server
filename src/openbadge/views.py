import simplejson, pytz, StringIO
import datetime, random, math
from decimal import Decimal
from dateutil.parser import parse as parse_date
from pytz import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from functools import wraps
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile

from .decorators import app_view
from .models import StudyGroup, StudyMember, Meeting, WeeklyGroupReport
import analysis
from django.conf import settings

from django.contrib.auth.decorators import user_passes_test


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

    meeting_info = simplejson.loads(log_file.readline())
    log_file.seek(0)

    meeting_uuid = meeting_info["uuid"]
    moderator_key = meeting_info["moderator"]
    members = meeting_info["members"]
    group_key = meeting_info["group"]
    start_time = parse_date(meeting_info["startTime"])
    meeting_location = meeting_info["location"]
    meeting_type = meeting_info["type"]
    meeting_description = meeting_info["description"]
    show_visualization = meeting_info["showVisualization"]

    is_complete = request.POST.get("isComplete") == 'true'
    end_time_string = request.POST.get("endTime")
    ending_method = request.POST.get("endingMethod", "")
    end_time = parse_date(end_time_string) if end_time_string else None

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

    meeting.members = simplejson.dumps(members)
    meeting.start_time = start_time
    meeting.type = meeting_type
    meeting.location = meeting_location
    meeting.description = meeting_description
    meeting.end_time = end_time if end_time else meeting.get_last_sample_time()
    meeting.is_complete = is_complete
    meeting.show_visualization = show_visualization
    meeting.ending_method = ending_method
    meeting.save()

    if meeting.is_complete and settings.SEND_POST_MEETING_SURVEY:
        analysis.post_meeting_analysis(meeting)

    return json_response(success=True)


@user_passes_test(lambda u: u.is_superuser)
def weekly_group_report(request, group_key, week_num):
    group = StudyGroup.objects.get(key=group_key)
    name = group.name

    info = WeeklyGroupReport.objects.get(group_key=group_key, week_num=week_num).to_dict()
    info['start_date'] = datetime.datetime.strptime(info['start_date'],"%Y-%m-%d").strftime("%A, %B %d")
    info['end_date'] = datetime.datetime.strptime(info['end_date'],"%Y-%m-%d").strftime("%A, %B %d")
    info['longest_meeting_date'] = datetime.datetime.strptime(info['longest_meeting_date'],"%A %Y-%m-%d").strftime("%A, %B %d")

    images = ['location_meeting_count','type_meeting_count','daily_meeting_time','daily_turns_rate','longest_meeting_turns']
    paths = {}
    for image in images:
        paths[image] = "img/weekly_group_reports/" + group_key + "/week_" + week_num +"_"+image+".png"

    return render(request, 'openbadge/report_template.html', {'paths':paths , 'info':info, 'name':name, 'week_num':week_num})
