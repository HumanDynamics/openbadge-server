import simplejson, pytz, StringIO
import os, datetime, random, math
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

from newGraph import groupStatGraph
from django.contrib.auth.decorators import user_passes_test

import ast

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

## APP views ###########################################################################################################

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

## Report views ########################################################################################################

#@user_passes_test(lambda u: u.is_superuser)
def weekly_group_report(request, group_key, week_num):

    try:
        info = WeeklyGroupReport.objects.get(group_key=group_key, week_num=week_num).to_dict()
        group = StudyGroup.objects.get(key=group_key)
        name = group.name
    except WeeklyGroupReport.DoesNotExist:
        return render(request, 'openbadge/report_template.html', {'exist':False, 'key':group_key, 'week_num':week_num})

    info['start_date'] = datetime.datetime.strptime(info['start_date'],"%Y-%m-%d").strftime("%A, %B %d")
    info['end_date'] = datetime.datetime.strptime(info['end_date'],"%Y-%m-%d").strftime("%A, %B %d")
    info['longest_meeting_date'] = datetime.datetime.strptime(info['longest_meeting_date'],"%A %Y-%m-%d").strftime("%A, %B %d")

    images = ['location_meeting_count','type_meeting_count','daily_meeting_time','daily_turns_rate','longest_meeting_turns']
    paths = {}
    for image in images:
        paths[image] = "img/weekly_group_reports/" + group_key + "/week_" + week_num +"_"+image+".png"

    report_week_num = str(int(week_num) + 2)
    return render(request, 'openbadge/report_template.html', {'exist':True, 'paths':paths , 'info':info, 'name':name, 'week_num':report_week_num})

@user_passes_test(lambda u: u.is_superuser)
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
	
	graph_path = settings.MEDIA_ROOT + '/tmp'
		
	try:
		os.mkdir(graph_path)
	except OSError:
		if not os.path.isdir(graph_path):
			raise
	
	metadata = groupStatGraph(durations, num_meetings, dates, names, graph_path)

	return render(request, 'reports/internal_report.html', {'metadata':metadata})


def h1_report(request, member_key):
    charts_path = settings.MEDIA_ROOT + '/h1_reports/charts/'
    p_chart_file_name = charts_path + member_key + '_participation_chart.txt'
    with open(p_chart_file_name, 'r') as out:
        h1_report_data = ast.literal_eval(out.read())
        
    s_chart_file_name = charts_path + member_key + '_satisfaction_chart.txt'
    with open(s_chart_file_name, 'r') as out:
        h1_report_data.update(ast.literal_eval(out.read()))
        
    a_chart_file_name = charts_path + member_key + '_all_chart.txt'
    with open(a_chart_file_name, 'r') as out:
        h1_report_data.update(ast.literal_eval(out.read()))

    member = StudyMember.objects.get(key=member_key)
    group = member.group
    member_names = {}
    for member in group.members.all():
        member_names[member.key] = member.name

    path = "../media/h1_reports/transitions/"
    transition_left_file_name = path + group.key + '_' + member_key + '_left.json'
    transition_right_file_name = path + group.key + '_' + member_key + '_right.json'
    s_left = ''
    s_right = ''
    with open(transition_left_file_name, 'r') as transitions_left:
        s_left = transitions_left.read()
    with open(transition_right_file_name, 'r') as transitions_right:
        s_right = transitions_right.read()
    for member_key, member_name in member_names.iteritems():
        s_left = s_left.replace(member_key, member_name)
        s_right = s_right.replace(member_key, member_name)
        h1_report_data['participation_script'] = h1_report_data['participation_script'].replace(member_key, member_name)
        
    graph_dict_left = ast.literal_eval(s_left)
    graph_left = simplejson.dumps(graph_dict_left)
    graph_dict_right = ast.literal_eval(s_right)
    graph_right = simplejson.dumps(graph_dict_right)
        
    misc_data = dict(member=member, group=group,
                     graph_left=graph_left, graph_right=graph_right)
    h1_report_data.update(misc_data)
    return render(request, 'reports/h1_report.html', h1_report_data)
