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
from .models import StudyGroup, StudyMember, Meeting
import analysis
from django.conf import settings


from django.contrib.auth.decorators import user_passes_test


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


def make_dates_dict(all_meetings):
    dates = {}
    #all meetings for a date
    for meeting in all_meetings:
        d = meeting.start_time.date()
        meetings = []
        current_info = dates.get(str(d),{})
        current_info['meetings'] = current_info.get('meetings',[]) + [meeting.uuid]
        #total duration of meetings for a date
        duration = (meeting.end_time - meeting.start_time)
        current_info['duration'] = current_info.get('duration',0) + duration.total_seconds()/3600 #hours
        #total number of meetings in for a date
        current_info['total'] = current_info.get('total',0) + 1
        dates[str(d)] = current_info
    return dates


@user_passes_test(lambda u: u.is_superuser)
def get_group(request, group_key):
    try:
        group = StudyGroup.objects.prefetch_related("members", "visualization_ranges").get(key=group_key)
        meetings = [meeting for meeting in group.meetings.all()]
        meetings_based_on_dates = make_dates_dict(meetings)
        members = [member for member in group.members.all()]
        return render(request, 'openbadge/get_group.html', {'info':group.to_dict(), 'members': members, 'meetings': meetings, 'meetings_based_on_dates': meetings_based_on_dates})
    except StudyGroup.DoesNotExist:
        return HttpResponse("no group found with Group Key")


@user_passes_test(lambda u: u.is_superuser)
def get_finished_meetings(request, group_key):

    if not group_key:
        raise Http404()

    try:
        group = StudyGroup.objects.prefetch_related("meetings").get(key=group_key)
    except StudyGroup.DoesNotExist:
        raise Http404()

    finished_meetings = [meeting for meeting in group.meetings.filter(is_complete=True).all()]
    return render(request, 'openbadge/get_meetings.html', {'heading': "Finished Meetings for Group "+group.name, 'dates': make_dates_dict(finished_meetings)})
    

@user_passes_test(lambda u: u.is_superuser)
def get_meetings(request):
    all_meetings = Meeting.objects.all()#.order_by('start_time') doesn't work..
    return render(request, 'openbadge/get_meetings.html', {'heading': "All Meetings by Date", 'dates': make_dates_dict(all_meetings)})


@user_passes_test(lambda u: u.is_superuser)
def get_groups(request):
    groups = StudyGroup.objects.all()
    return render(request, 'openbadge/get_groups.html', {'groups': groups})


@user_passes_test(lambda u: u.is_superuser)
def get_meeting(request, uuid):
    try:
        meeting = Meeting.objects.get(uuid=uuid)
        info = {}
        info['uuid'] = uuid
        info['group'] = meeting.group.name
        info['members'] = meeting.members
        info['start_time'] = str(meeting.start_time)
        info['end_time'] = str(meeting.end_time)
        info['duration'] = str(meeting.end_time - meeting.start_time)
        info['moderator'] = meeting.moderator.name
        info['type'] = meeting.type
        info['location'] = meeting.location
        info['description'] = meeting.description
        info['is_complete'] = meeting.is_complete
        info['show_visualization'] = meeting.show_visualization
        info['ending_method'] = meeting.ending_method
        return render(request, 'openbadge/get_meeting.html', {'info':info})
    except Meeting.DoesNotExist:
        return HttpResponse("can't find meeting with UUID")
