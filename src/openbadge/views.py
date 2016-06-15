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

import json
import pandas as pd
import mpld3, seaborn as sns
import numpy as np
import copy
import itertools
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator,MinuteLocator,DateFormatter, drange

import os.path

from django.contrib.auth.decorators import user_passes_test

from datetime import timedelta


BASE = os.path.dirname(os.path.abspath(__file__))
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
        #total_duration_of_meetings for a date
        duration = (meeting.end_time - meeting.start_time)
        current_info['duration'] = current_info.get('duration',0) + duration.total_seconds()/3600 #hours
        #total number of meetings in for a date
        current_info['total'] = current_info.get('total',0) + 1
        dates[str(d)] = current_info
    return dates

def str_to_utc(time):
    time_format = "%Y-%m-%d"
    if isinstance(time, str):
        time = datetime.datetime.strptime(time, time_format)
        return time
    else:
        return time

def get_meeting_date(start_date, end_date):
    dates = []
    start_date = str_to_utc(start_date)
    end_date = str_to_utc(end_date)
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)
    meetings = []
    for date in daterange(start_date, end_date):
        date = date.date()
        meetings = meetings + [meeting for meeting in Meeting.objects.filter(start_time__startswith=date)]
    return meetings
    ##############################

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

'''
def report(request):
    meetings = get_meeting_date2("2016-06-13","2016-06-15")
    
    return render(request, 'openbadge/report2.html', {'meetings':meetings})
'''

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

def sample2data(input_file_name,to_csv=False,datetime_index=True,resample=True):
    with open(input_file_name,'r') as input_file:
        raw_data = input_file.readlines() #This is a list of strings
        meeting_metadata = json.loads(raw_data[0]) #Convert the header string into a json object
        batched_sample_data = map(json.loads,raw_data[1:]) #Convert the raw sample data into a json object
        #print batched_sample_data[0]

    sample_data = []

    for j in range(len(batched_sample_data)):
        batch = {}
        batch.update(batched_sample_data[j]) #Create a deep copy of the jth batch of samples
        samples = batch.pop('samples')
        reference_timestamp = batch.pop('timestamp')*1000+batch.pop('timestamp_ms') #reference timestamp in milliseconds
        sampleDelay = batch.pop('sampleDelay')
        numSamples = batch.pop('numSamples')
        for i in range(numSamples):
            sample = {}
            sample.update(batch)
            sample['signal'] = samples[i]
            sample['timestamp'] = reference_timestamp + i*sampleDelay
            sample_data.append(sample)

    df_sample_data = pd.DataFrame(sample_data)
    df_sample_data['datetime'] = pd.to_datetime(df_sample_data['timestamp'], unit='ms')
    del df_sample_data['timestamp']

    df_sample_data.sort_values('datetime')

    if(datetime_index):
        df_sample_data.set_index(pd.DatetimeIndex(df_sample_data['datetime']),inplace=True)
        #The timestamps are in UTC. Convert these to EST
        #df_sample_data.index = df_sample_data.index.tz_localize('utc').tz_convert('US/Eastern')
        df_sample_data.index.name = 'datetime'
        del df_sample_data['datetime']
        if(resample):
            grouped = df_sample_data.groupby('member')
            df_resampled = grouped.resample(rule=str(sampleDelay)+"L").mean()

    if(to_csv):
        output_file_name = input_file_name.split(".")[0] + ".csv"
        print "DataFrame written to "+output_file_name

        if(resample):
            df_resampled.to_csv(output_file_name)
        else:
            df_sample_data.to_csv(output_file_name)
            return None
    else:
        if(resample):
            # Optional: Add the meeting metadata to the dataframe
            df_resampled.metadata = meeting_metadata
            return df_resampled
        else:
            # Optional: Add the meeting metadata to the dataframe
            df_sample_data.metadata = meeting_metadata
            return df_sample_data

def is_speaking(df_meeting,sampleDelay = 50):
    frame_size = 1000 #milliseconds
    median_window = 2*60*1000 #milliseconds
    clipping_value = 120 #Maximum value of volume above which the signal is assumed to have non-speech external noise
    avg_speech_power_threshold = 42
    #Calculate the rolling median and subtract this value from the volume
    df_median = df_meeting.apply(lambda x:pd.rolling_median(x, window=int(median_window/sampleDelay), min_periods=1))
    df_normalized = df_meeting - df_median
    #Calculate power and apply avg speech power threshold
    df_energy = df_normalized.apply(np.square)
    df_power = df_energy.apply(lambda x:pd.rolling_mean(x, window=int(frame_size/sampleDelay), min_periods=1))
    df_is_speech = df_power > avg_speech_power_threshold
    #df_is_speech.plot(kind='area',subplots=True);plt.show()
    return df_is_speech

def get_all_segments(x_series):
    #Given a time series store the length, starting and stopping indices of segments having the same value throughout
    #In the case of a boolean series find all the continuous True segments and false segments
    total_samples = len(x_series)
    i=0
    segments= []
    current_segment = {'length':0,'start':0,'start_time':x_series.index[0]}
    while(i<total_samples):
        current_value = x_series[i]
        if(i==0):
            current_segment['value'] = current_value
            previous_value = current_value
            
        if((previous_value != current_value) or (i==total_samples-1)):
            current_segment['stop'] = i
            current_segment['stop_time'] = x_series.index[i]
            segments.append(copy.deepcopy(current_segment))
            current_segment = {'length':1,'start':i,'start_time':x_series.index[i],'value':current_value}
        else:
            current_segment['length']+=1
        i=i+1
        previous_value = current_value
    return pd.DataFrame(segments)
            
        

def get_stitched(df_is_speech,min_talk_length=2000,min_gap_size=500,sampleDelay = 50):
    min_talk_length_samples = int(min_talk_length/sampleDelay)
    min_gap_size_samples = int(min_gap_size/sampleDelay)
    
    df_is_gap = df_is_speech.copy()
    #df_is_gap = df_is_gap.apply(lambda x:x and False)
    
    for member in df_is_speech.columns.values:
        df_is_gap[member] = True # Initialise all values to True
        
        #First find all the gaps greater than or equal to min_gap_size (milliseconds)
        #Set the corresponding samples to False in df_is_gap
        all_segments = get_all_segments(df_is_speech[member])
        filtered_rows = ~(all_segments['value']) & (all_segments['length']>=min_gap_size_samples)
        all_segments = all_segments[filtered_rows]
        #mark large gaps with a false
        for index, row in all_segments.iterrows():
            start = row['start']
            stop = row['stop']
            df_is_gap[member][start:stop] = False
            
        #Then find all the segments which are less than min_talk_length (milliseconds and remove them)
        all_segments = get_all_segments(df_is_gap[member])
        filtered_rows = (all_segments['value']) & (all_segments['length']<min_talk_length_samples)
        all_segments = all_segments[filtered_rows]
        #mark small speaking segments with a false
        for index, row in all_segments.iterrows():
            start = row['start']
            stop = row['stop']
            df_is_gap[member][start:stop] = False
            
    return df_is_gap

def get_speaking_stats(df_meeting,sampleDelay = 50):
    #This function uses the data from a meeting to return 
    ####a.the number of turns per speaker per minute
    ####b.the total speaking time
    #Use speaking/not speaking function
    #Use stitching function
    #Expected input: A dataframe with a datetime index and one column per badge. 
    #Each column contains a time-series of absolute value speech volume samples
    df_is_speech = is_speaking(df_meeting)
    df_stitched = get_stitched(df_is_speech)
    all_stats=[]
    for member in df_stitched.columns.values:
        current_member = {}
        current_member['member'] = member
        all_segments = get_all_segments(df_stitched[member])
        filtered_rows = all_segments['value'] == True
        all_segments = all_segments[filtered_rows]
        current_member['totalTurns'] = len(all_segments)
        current_member['totalSpeakingTime'] = np.sum(all_segments['stop_time']-all_segments['start_time']) if len(all_segments)>0 else datetime.timedelta(0)
        all_stats.append(current_member)
        
    return all_stats

def get_speaking_series(df_meeting,sampleDelay = 50):
    def custom_resampler(array_like):
        return len([ sum( 1 for _ in group ) for key, group in itertools.groupby(array_like) if key ])

    df_is_speech = is_speaking(df_meeting)
    df_stitched = get_stitched(df_is_speech)
    df_stitched = df_stitched.resample('1T').apply(custom_resampler)
    
    return df_stitched

@user_passes_test(lambda u: u.is_superuser)
def data_process(request):
	scale = 3.0
	x_fontsize =10
	y_fontsize =10 
	title_fontsize = 14
        ######NEED TO ADD START_DATE AND END_DATE ARGS#########
        start_date = "2016-06-13"
        end_date = "2016-06-15"
	
	groups_meeting_data = {} # This will be a list of data frames
	input_file_names = [meeting.log_file.path for meeting in get_meeting_date(start_date, end_date)]
                
                
        for input_file_name in input_file_names:
	    group = input_file_name.split("/")[-2].split("_")[0]
	    if(not group in groups_meeting_data):
	        groups_meeting_data[group] = []
	    df_meeting = sample2data(input_file_name)
	    groups_meeting_data[group].append(df_meeting)
            
	
        df_metadata = pd.DataFrame()
	for group in groups_meeting_data:
	    #Do this for each group
    	    group_meeting_data = groups_meeting_data[group]
	    for df_meeting in group_meeting_data:
	        #Do this for each meeting of the group
	        #
	        ##Store the metadata for the meeting in a dataframe format for easier aggregation and plotting
	        metadata = {}
	        metadata.update(df_meeting.metadata)
	        df_meeting=pd.pivot_table(df_meeting.reset_index(),index='datetime',columns='member',values='signal').dropna()
	        df_meeting.index = df_meeting.index - np.timedelta64(4, 'h') # Convert UTC to EST
	        start_time = df_meeting.index[0]
	        end_time = df_meeting.index[-1]
	        metadata["startTime"] = start_time
	        metadata["endTime"] = end_time
	        metadata["totalMeetingTime"] = end_time - start_time
	        #Calculate number of turns here
	        members_stats = get_speaking_stats(df_meeting)
	        del metadata['members']
	        for member_stats in members_stats:
	            member_stats.update(metadata)
	        #Calculate speaking time per participant here
	        df_metadata = df_metadata.append(pd.DataFrame(members_stats))
	    df_metadata = df_metadata.reset_index()
	    del df_metadata['index']
	
	df_groups = df_metadata.groupby('group')
	datetime2str = lambda x:x.strftime('%Y-%m-%d %a')
	for group_name,group_data in df_groups:
	    dict_plotdata = {}
	    dict_plotdata['group_name'] = group_name
	    print "Meeting report for study group "+group_name
	    print "\nTotal number of meetings"
	    print pd.Series.nunique(group_data['uuid'])
	    dict_plotdata['total_meeting_count']=pd.Series.nunique(group_data['uuid'])
	    print "\nTotal number of meetings by day"
	    print group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    dict_plotdata['daily_meeting_count']= group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    print "\nTotal number of meetings by location"
	    print "\n",group_data.groupby(['location']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    dict_plotdata['location_meeting_count']=group_data.groupby(['location']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    print "\nTotal number of meetings by type"
	    print "\n",group_data.groupby(['type']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    dict_plotdata['type_meeting_count']=group_data.groupby(['type']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})
	    print "Total number of turns taken this week"
	    print "\n",np.sum(group_data["totalTurns"])
	    dict_plotdata['total_turns_count'] = np.sum(group_data["totalTurns"])
	    
	    print "\nTotal speaking time (in minutes) by day"
	    dict_plotdata['daily_speaking_time'] = group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"totalSpeakingTime": lambda x:sum(x,datetime.timedelta(0))})
	    dict_plotdata['daily_speaking_time']['totalSpeakingTime'] = dict_plotdata['daily_speaking_time']['totalSpeakingTime'].apply(lambda x:x.days*24*60+x.seconds//60)#.to_dict(orient='split')
	    print dict_plotdata['daily_speaking_time']
	    
	    dict_plotdata['total_speaking_time'] = np.sum(dict_plotdata['daily_speaking_time']['totalSpeakingTime'])
	    
	    print "\nTotal duration of meetings (in minutes) by day"
	    dict_plotdata['daily_meeting_time'] = group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"totalMeetingTime": np.sum})
	    dict_plotdata['daily_meeting_time']['totalMeetingTime'] = dict_plotdata['daily_meeting_time']['totalMeetingTime'].apply(lambda x:x.days*24*60+x.seconds//60)#.to_dict(orient='split')
	    print dict_plotdata['daily_meeting_time']
	    
	    dict_plotdata['total_duration_of_meetings'] = np.sum(dict_plotdata['daily_meeting_time']['totalMeetingTime'])
	    dict_plotdata['avg_speaking_time'] = dict_plotdata['total_speaking_time']*60/dict_plotdata['total_duration_of_meetings']

	    print "\nTotal number of turns taken by day"
	    print "\n",group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"totalTurns": np.sum})#.to_dict(orient='split')
	    dict_plotdata['daily_turns_count'] = group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"totalTurns": np.sum})#.to_dict(orient='split')
	    dict_plotdata['daily_turns_rate'] = dict_plotdata['daily_turns_count']['totalTurns'].divide(dict_plotdata['daily_meeting_time']['totalMeetingTime']) #per minute
	    
	    print "Number of turns taken per minute for the longest group meeting this week"
	    longest_meeting = group_data.loc[group_data['totalMeetingTime'].argmax()]['uuid']
	    group_meeting_data = groups_meeting_data[group_name]
	    for df in group_meeting_data:
	        if(df.metadata['uuid']==longest_meeting):
	            df_meeting=pd.pivot_table(df.reset_index(),index='datetime',columns='member',values='signal').dropna()
	            df_meeting.index = df_meeting.index - np.timedelta64(4, 'h') # Convert UTC to EST
	            dict_plotdata['longest_meeting_date'] = pd.to_datetime(str(df_meeting.index.values[0])).strftime('%A %Y-%m-%d')
	            df_meeting_turns = get_speaking_series(df_meeting)
	            df_meeting_turns['total'] = df_meeting_turns.sum(axis=1)
	            break
	    dict_plotdata['longest_meeting_turns'] = df_meeting_turns['total']
	    
	    print "Number of participants per meeting:"
	    print group_data.groupby('uuid')['member'].count()
	    dict_plotdata['meeting_member_count'] = group_data.groupby('uuid')['member'].count()
	    dict_plotdata['avg. member count'] = np.mean(dict_plotdata['meeting_member_count'])
	
            ax1 = dict_plotdata['type_meeting_count']['meeting_count'].plot.pie(legend=True,labels=None,autopct='%.1f%%')
            ax1.set_aspect('equal')
            fig_type = ax1.get_figure()
            plt.ylabel('')
            plt.xlabel('')
            plt.tight_layout()
            mpld3.fig_to_html(fig_type)

            plt.savefig(os.path.join(BASE, "img/"+dict_plotdata['group_name']+"_type_meeting_count.png"))
            plt.gcf().clear()
            
            ax2 = dict_plotdata['location_meeting_count']['meeting_count'].plot.pie(legend=True,labels=None,autopct='%.1f%%')
            ax2.set_aspect('equal')
            fig_loc = ax2.get_figure()
            #plt.title('Meetings by location',fontsize=title_fontsize)
            plt.ylabel('')
            plt.xlabel('')
            plt.tight_layout()
            mpld3.fig_to_html(fig_loc)
            plt.savefig(os.path.join(BASE, "img/"+dict_plotdata['group_name']+"_location_meeting_count.png"))
            plt.gcf().clear()
	
            ax3 = dict_plotdata['daily_meeting_time'].plot(kind='bar',rot=45,figsize=(scale*2.5, scale*1.5))
            fig_meet_time = ax3.get_figure()
            mpld3.fig_to_html(fig_meet_time)
            #plt.title('Meeting duration by day',fontsize=title_fontsize)
            plt.ylabel('Total meeting duration (minutes)',fontsize=y_fontsize)
            plt.xlabel('Date', fontsize=x_fontsize)
            plt.tight_layout()
            plt.savefig(os.path.join(BASE, "img/"+dict_plotdata['group_name']+"_daily_meeting_time.png"))
            plt.gcf().clear()
	
            ax5 = dict_plotdata['daily_turns_rate'].plot(kind='bar',rot=45,figsize=(scale*2.5,scale*1.5))
            fig_turns_count = ax5.get_figure()
            #plt.title('Number of turns by day',fontsize=title_fontsize)
            plt.ylabel('Number of turns taken per hour',fontsize=y_fontsize)
            plt.xlabel('Date', fontsize=x_fontsize)
            plt.tight_layout()
            mpld3.fig_to_html(fig_turns_count)
            plt.savefig(os.path.join(BASE, "img/"+dict_plotdata['group_name']+"_daily_turns_rate.png"))
            plt.gcf().clear()
            
            minorLocator = HourLocator()
            ax4 = dict_plotdata['longest_meeting_turns'].resample('S').interpolate(method='cubic').plot(figsize=(scale*5,scale))#
            ax4.xaxis.set_minor_locator(minorLocator)
            fig_meet_turns = ax4.get_figure()
            #plt.title('Number of turns per minute in the longest meeting',fontsize=title_fontsize)
            plt.ylabel('Average number of turns taken',fontsize=y_fontsize)
            plt.xlabel('Time', fontsize=x_fontsize)
            plt.tight_layout()
            mpld3.fig_to_html(fig_meet_turns)
            plt.savefig(os.path.join(BASE, "img/"+dict_plotdata['group_name']+"_longest_meeting_turns.png"))
            plt.gcf().clear()

            dict_plotdata_min = {}
            for key in ['total_meeting_count','total_duration_of_meetings','avg_speaking_time','longest_meeting_date','group_name']:
                dict_plotdata_min[key] = dict_plotdata[key]
            with open(os.path.join(BASE, 'dict_plotdata/'+dict_plotdata['group_name']+'_dict_plotdata.txt'),'w') as output_file:
                output_file.write(json.dumps(dict_plotdata_min))
        return HttpResponse("Successfully generated plots.")

@user_passes_test(lambda u: u.is_superuser)
def report(request, group_name):
    #data_process()
    with open(os.path.join(BASE, 'dict_plotdata/'+group_name+'_dict_plotdata.txt'),'r') as result_file:
        dict_string = result_file.read()
    dict_plotdata = json.loads(dict_string)
    
    images = ['location_meeting_count','type_meeting_count','daily_meeting_time','daily_turns_rate','longest_meeting_turns']
    aggregate_keys = ['total_meeting_count','total_duration_of_meetings','avg_speaking_time','longest_meeting_date']

    info = {}
    info['group_name'] = dict_plotdata['group_name']
    for image in images:
        #info[image] = os.path.join(BASE, "img/"+dict_plotdata['group_name']+"_"+image+".png")
        info[image] = dict_plotdata['group_name']+"_"+image+".png"
    for key in aggregate_keys:
        info[key] = str(dict_plotdata[key])
        
    return render(request, 'openbadge/report_template3.html', {'info': info})
