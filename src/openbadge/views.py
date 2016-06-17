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
import analysis
from django.conf import settings

from createGraph import individualGraph, aggregateGraph
from newGraph import groupStatGraph

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


@app_view
@api_view(['GET'])
def get_group(request, group_key):

    if not group_key:
        return json_response(success=False)

    try:
        group = StudyGroup.objects.prefetch_related("members", "visualization_ranges").get(key=group_key)
    except StudyGroup.DoesNotExist:
        return json_response(success=False)

    return json_response(success=True, group=group.to_dict())


@app_view
@api_view(['GET'])
def get_finished_meetings(request, group_key):

    if not group_key:
        raise Http404()

    try:
        group = StudyGroup.objects.prefetch_related("meetings").get(key=group_key)
    except StudyGroup.DoesNotExist:
        raise Http404()

    finished_meetings = [meeting.uuid for meeting in group.meetings.filter(is_complete=True).all()]

    return json_response(success=True, finished_meetings=finished_meetings)
''' 
def internal_report(request, period): 
	
	groups = StudyGroup.objects.all().order_by('name')
	
	meetings = [{study_group.name:Meeting.objects.filter(is_complete=True,
			group__name=study_group.name, start_time__gt = datetime.datetime.now()- datetime.timedelta(days=int(period)-1),
			end_time__lte = datetime.datetime.now()).all().order_by('start_time')}
			for study_group in groups]
	
	metadata = individualGraph(meetings, datetime.datetime.now(), int(period))
	metadata['period'] = period
	
	aggregateGraph(metadata['agg_duration'], metadata['days'])
		
	return render(request, 'reports/internal_report.html', {'metadata':metadata})
'''

def internal_report(request):
	
	groups = StudyGroup.objects.all().order_by('name')
	
	durations = []
	num_meetings = []
	names = []
	
	dates = [datetime.date(2016,6,13) + datetime.timedelta(days=i) for i in xrange(28)]
	
	for s_group in groups:
		meetings = Meeting.objects.filter(group__key = s_group.key, is_complete=True).all()
		
		num_meet_temp = []
		time_meet_temp = []
		
		for current in dates:
			meets = [meet for meet in meetings
				if (meet.start_time.year == current.year and
				meet.start_time.month == current.month and
				meet.start_time.day == current.day)]
			
			num_meet_temp.append(len(meets))
			times = [entry.end_time - entry.start_time for entry in meets]
			time_meet_temp.append((sum(times, datetime.timedelta()).total_seconds())/3600.0)
			
		num_meetings.append(num_meet_temp)
		durations.append(time_meet_temp)
		names.append(s_group.name)
	
	metadata = groupStatGraph(durations, num_meetings, dates, names)

	return render(request, 'reports/internal_report.html', {'metadata':metadata})
