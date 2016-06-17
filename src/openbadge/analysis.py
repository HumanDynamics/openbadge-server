import smtplib, os, simplejson, datetime, csv, pytz
import time

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

from email.header import Header

import passwords

from django.template import loader

from .models import StudyGroup, StudyMember, VisualizationRange, Meeting, WeeklyGroupReport
from django.conf import settings
import urllib

import json
import pandas as pd
import mpld3, seaborn as sns
import numpy as np
import copy
import itertools
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator,MinuteLocator,DateFormatter, drange

import time

#from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site

def post_meeting_analysis(meeting):
    member_ids = simplejson.loads(meeting.members)
    members = meeting.group.members.filter(key__in=member_ids).all()
    #recipients = [member.email for member in members]

    #TODO: do analysis
    #chunks = meeting.get_chunks()
    #total_samples = sum([sum(chunk["samples"]) for chunk in chunks])
    #analysis_results = dict(total_samples=total_samples)


    for member in members:
        send_post_meeting_survey(meeting,member)
        time.sleep(.5)


def send_post_meeting_survey(meeting,member):
    eastern = pytz.timezone('US/Eastern')
    start_time = meeting.start_time.astimezone(eastern)

    template = loader.get_template("email/end_meeting_email.html")
    template_plain = loader.get_template("email/end_meeting_email_plain.html")

    f = {'memberKey': member.key, 'meetingUUID': meeting.uuid,
         'meetingStartTime': start_time.strftime('%-I:%M %p, %B %-d, %Y')}
    url = settings.POST_MEETING_SURVEY_URL + '?' + urllib.urlencode(f);

    body = template.render(dict(meeting=meeting,  start_time=start_time, member=member, survey_url=url))
    body_plain = template_plain.render(dict(meeting=meeting, start_time=start_time, member=member, survey_url=url))

    send_email(passwords.EMAIL_USERNAME, passwords.EMAIL_PASSWORD, member.email,
               "RoundTable Group Meeting Survey | " + start_time.strftime('%B %-d, %Y at %-I:%M %p'), body, body_plain)


def send_weekly_email(group, week_num):

    members = group.members.all()
    recipients = [member.email for member in members]

    #start_time = datetime.datetime.now() - datetime.timedelta(days=7)
    #meetings = group.meetings.filter(start_time__gte=start_time)

    total_hours = 0
    for meeting in Meeting.objects.all():
        duration = (meeting.end_time - meeting.start_time).total_seconds()/3600
        total_hours += duration
    total_hours = int(total_hours)
    ###########CHANGE URL TO INCLUDE ACTUAL HOST#####################

    #request = None
    #print(settings.SITE_ID)
    #full_url = ''.join(['http://', get_current_site(request).domain, obj.get_absolute_url()])
    #print (full_url)
    #return

    #url = "http://127.0.0.1:8000/weekly_group_report/"+group.key+"/"+week_num
    url = "http://" + settings.SITE_ID + "/"+group.key+"/"+week_num
    #settings.SITE_ID returns cynthia.media.mit.edu on my laptop
    #hopefully, settings.SITE_ID on production server is openbadgeprod.media.mit.edu ... 

    template = loader.get_template("email/weekly_report_email.html")
    body = template.render(dict(group=group, week_num=week_num, url=url, total_hours=total_hours))

    for recipient in recipients:
        send_email(passwords.EMAIL_USERNAME, passwords.EMAIL_PASSWORD, recipient, "Roundtable Weekly Summary for " +group.name+ " for Week " +week_num, body)
        time.sleep(.3)
   

# https://docs.python.org/2/library/email-examples.html
def send_email(user, pwd, recipient, subject, body, body_plain = None):

    FROM = user
    TO = [recipient]

    msg = MIMEMultipart("alternative", _charset="UTF-8")

    msg['FROM'] = FROM
    msg['To'] = recipient
    msg['Subject'] = Header(subject, "utf-8")

    if body_plain:
        msg.attach(MIMEText(body_plain, 'plain'))

    msg.attach(MIMEText(body, 'html', 'UTF-8'))

    try:
        server = smtplib.SMTP(passwords.EMAIL_SMTP, 587)
        server.ehlo()
        server.starttls()
        if pwd:
            server.login(user, pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        print 'sent email to', recipient
    except Exception, e:
        import traceback
        traceback.print_exc()
        print "failed to send mail"


def load_users_from_csv(filename):
    '''
    Assumes a CSV with a header row and has the columns:
    email, group, name, badge
    '''

    num_new_groups = 0
    num_new_members = 0

    groups = {group.name: group for group in StudyGroup.objects.all()}
    members = {member.email: member for member in StudyMember.objects.all()}
    new_group_keys = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            # only create new users if we don't have one with the same email
            if row['email'] not in members.keys():

                # create a new group for the member if we don't have one already
                print(row)
                if row['group'] not in groups.keys():
                    group = StudyGroup(name=row['group'])
                    group.save()
                    new_group_keys.append(group.key)

                    print("Created new group {}".format(group.key))
                    groups[group.name] = group
                    num_new_groups += 1

                # create the new user
                group = groups[row['group']]
                member = StudyMember(name=row['name'],
                                     email=row['email'],
                                     badge=row['badge'],
                                     group=group)
                member.save()
                members[member.email] = member
                num_new_members += 1

    return num_new_members, num_new_groups, new_group_keys


def set_visualization_ranges(group_key,filename):
    '''
    Assumes a CSV with a header row and has the columns:
    start,end
    where the dates are in this format - 2016-06-07 16:37:12
    Note - time is in UTC time
    '''
    group = StudyGroup.objects.get(key=group_key)

    vrs = VisualizationRange.objects.filter(group=group)
    for a in vrs:
        print(a.to_dict())
        a.delete()

    num_new_vr = 0
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            startTime =  datetime.datetime.strptime(row['start'], "%Y-%m-%d %H:%M:%S")
            endtime =  datetime.datetime.strptime(row['end'], "%Y-%m-%d %H:%M:%S")
            vr = VisualizationRange.objects.create(group=group, start=startTime,end=endtime)
            vr.save()
            num_new_vr += 1

    return num_new_vr


def get_week_dates(week_num):

    #Monday to Sunday, starting from Mon 2016-06-13
    time_format = "%Y-%m-%d"
    day1 = datetime.datetime.strptime("2016-06-13", time_format)
    start_date = day1 + datetime.timedelta(days = (week_num-1)*7)
    end_date = start_date + datetime.timedelta(days = 6)
    start_date = datetime.datetime.strftime(start_date, time_format) #removes 00:00:00 at the end
    end_date = datetime.datetime.strftime(end_date, time_format)
    return (start_date, end_date)


# GENERATE CHARTS FOR WEEKLY GROUP REPORTS:

def str_to_utc(time):
    time_format = "%Y-%m-%d"
    if isinstance(time, str):
        time = datetime.datetime.strptime(time, time_format)
        return time
    else:
        return time

def get_meetings_date(start_date, end_date):
    dates = []
    start_date = str_to_utc(start_date)
    end_date = str_to_utc(end_date)
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + datetime.timedelta(n)
    meetings = []
    for date in daterange(start_date, end_date):
        date = date.date()
        meetings = meetings + [meeting for meeting in Meeting.objects.filter(start_time__startswith=date)]
    return meetings



def get_meetings_date_group(start_date, end_date, group_key):
    dates = []
    start_date = str_to_utc(start_date)
    end_date = str_to_utc(end_date)
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + datetime.timedelta(n)
    meetings = []
    group = StudyGroup.objects.get(key=group_key)
    for date in daterange(start_date, end_date):
        date = date.date()
        meetings = meetings + [meeting for meeting in Meeting.objects.filter(start_time__startswith=date, group=group)]
    return meetings






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
    if len(sample_data)==0:
        return None
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
        #print "DataFrame written to "+output_file_name

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

##########NEW

def is_speaking(df_meeting,sampleDelay = 50):
    frame_size = 1000 #milliseconds
    median_window = 2*60*1000 #milliseconds
    median_window = int(median_window/sampleDelay)
    power_window = int(frame_size/sampleDelay)
    clipping_value = 120 #Maximum value of volume above which the signal is assumed to have non-speech external noise
    df_meeting = df_meeting.clip(upper=clipping_value)
    avg_speech_power_threshold = 42
    #Calculate the rolling median and subtract this value from the volume
    df_median = df_meeting.apply(lambda x:x.rolling(min_periods=1,window=median_window,center=False).median())
    df_normalized = df_meeting - df_median
    #Calculate power and apply avg speech power threshold
    df_energy = df_normalized.apply(np.square)
    df_power = df_energy.apply(lambda x:x.rolling(window=power_window, min_periods=1,center=False).mean())
    df_is_speech = df_power > avg_speech_power_threshold
    #df_is_speech.plot(kind='area',subplots=True);plt.show()
    df_max_power = df_power.apply(np.max,axis=1)
    df_is_winner = df_power.apply(lambda x:x==df_max_power) #Find the badge with the highest power reading at every sample interval and declare it to be the main speaker
    #The assumption here is that there is only one speaker at any given time

    df_is_speech = df_is_speech & df_is_winner
    return df_is_speech

def fill_boolean_segments(x_series,min_length,value):
    #Given a boolean series fill in all value (True or False) sequences less than length min_length with their inverse
    total_samples = len(x_series)
    not_value = not value
    i=0
    length=0
    start=0
    while(i<total_samples):
        current_value = x_series[i]
        if(i==0):
            previous_value = current_value

        if((previous_value != current_value) or (i==total_samples-1)):
            stop = i
            if(length<min_length and previous_value==value):
                x_series[start:stop] = not_value
            length=1
            start=i
        else:
            length+=1
        i=i+1
        previous_value = current_value



def get_stitched(df_is_speech,min_talk_length=2000,min_gap_size=500,sampleDelay = 50):
    min_talk_length_samples = int(min_talk_length/sampleDelay)
    min_gap_size_samples = int(min_gap_size/sampleDelay)
    df_is_gap = df_is_speech.copy()

    for member in df_is_speech.columns.values:
        #First fill all the gaps less than min_gap_size (milliseconds)
        #Set the corresponding samples to True in df_is_gap
        fill_boolean_segments(df_is_gap[member],min_gap_size_samples,False)
        #Then find all the True segments which are less than min_talk_length (milliseconds) and invert them
        fill_boolean_segments(df_is_gap[member],min_talk_length_samples,True)

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
    #df_is_speech.plot(kind='area',subplots=True);plt.show()
    df_stitched = get_stitched(df_is_speech)
    #df_stitched.plot(kind='area',subplots=True);plt.show()
    all_stats=[]
    for member in df_stitched.columns.values:
        current_member = {}
        current_member['member'] = member
        current_member['totalTurns'] = len([ sum( 1 for _ in group ) for key, group in itertools.groupby(df_stitched[member]) if key ])
        #print sum(df_stitched[member])*sampleDelay
        current_member['totalSpeakingTime'] = datetime.timedelta(milliseconds=sum(df_stitched[member])*sampleDelay) #if len(all_segments)>0 else datetime.timedelta(0)
        #current_member['total_speaking_time'] = np.sum(all_segments['length'])*sampleDelay
        all_stats.append(current_member)
    return all_stats

def get_speaking_series(df_meeting,sampleDelay = 50):
    def custom_resampler(array_like):
        return len([ sum( 1 for _ in group ) for key, group in itertools.groupby(array_like) if key ])

    df_is_speech = is_speaking(df_meeting)
    #df_is_speech.plot(kind='area',subplots=True);plt.show()
    df_stitched = get_stitched(df_is_speech)
    #df_stitched.plot(kind='area',subplots=True);plt.show()
    df_stitched = df_stitched.resample('1T').apply(custom_resampler)

    return df_stitched


def data_process(week_num, group_key=None):

        print("Start: "+str(time.time()))

        matplotlib.rcParams['font.size'] = 18    
	scale = 3.0
	x_fontsize = 10
	y_fontsize = 10 
	title_fontsize = 14
        start_date, end_date = get_week_dates(int(week_num))
        idx = pd.date_range(start_date,end_date)
	
	groups_meeting_data = {} # This will be a list of data frames
        if group_key:
            input_file_names = [meeting.log_file.path for meeting in get_meetings_date_group(start_date, end_date, group_key)]
        else:
            input_file_names = [meeting.log_file.path for meeting in get_meetings_date(start_date, end_date)]

        for input_file_name in input_file_names:
	    group = input_file_name.split("/")[-2].split("_")[0]
	    if(not group in groups_meeting_data):
	        groups_meeting_data[group] = []
	    df_meeting = sample2data(input_file_name)
	    groups_meeting_data[group].append(df_meeting)

        #print("2: "+str(time.time()))
        #i = 0
	
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
                #df_meeting.index = df_meeting.index.tz_localize('UTC').tz_convert('US/Eastern')
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

            print("Metadata stored for "+group)

            #i += 1
            #print ("2." + str(i) + ": Group " + group + " " +str(time.time()))

        #i = 0
	
        if 'group' in df_metadata:
            df_groups = df_metadata.groupby('group')
        else:
            print("Error: No meetings occured in Week "+week_num)
            return

	datetime2str = lambda x:x.strftime('%Y-%m-%d %a')
	for group_name,group_data in df_groups:
	    dict_plotdata = {}
	    dict_plotdata['group_name'] = group_name
	    #print "Meeting report for study group "+group_name
	    #print "\nTotal number of meetings"
	    #print pd.Series.nunique(group_data['uuid'])
	    dict_plotdata['total_meeting_count']=pd.Series.nunique(group_data['uuid'])
	    #print "\nTotal number of meetings by day"
	    #print group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    dict_plotdata['daily_meeting_count']= group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    #print "\nTotal number of meetings by location"
	    #print "\n",group_data.groupby(['location']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    dict_plotdata['location_meeting_count']=group_data.groupby(['location']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    #print "\nTotal number of meetings by type"
	    #print "\n",group_data.groupby(['type']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})#.to_dict(orient='split')
	    dict_plotdata['type_meeting_count']=group_data.groupby(['type']).agg({"uuid": pd.Series.nunique}).rename(columns={'uuid':'meeting_count'})
	    #print "Total number of turns taken this week"
	    #print "\n",np.sum(group_data["totalTurns"])
	    dict_plotdata['total_turns_count'] = np.sum(group_data["totalTurns"])
	    
	    #print "\nTotal speaking time (in minutes) by day"
	    dict_plotdata['daily_speaking_time'] = group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"totalSpeakingTime": lambda x:sum(x,datetime.timedelta(0))})

            #print("Daily speaking time: "+str(dict_plotdata['daily_speaking_time']))

	    dict_plotdata['daily_speaking_time']['totalSpeakingTime'] = dict_plotdata['daily_speaking_time']['totalSpeakingTime'].apply(lambda x:x.days*24*60+x.seconds//60)#.to_dict(orient='split')
	    #print dict_plotdata['daily_speaking_time']
	    

	    dict_plotdata['total_speaking_time'] = np.sum(dict_plotdata['daily_speaking_time']['totalSpeakingTime'])
	    
            dict_plotdata['daily_meeting_time'] = group_data.groupby(pd.Grouper(key='startTime',freq='1D')).agg({"totalMeetingTime": np.sum})
            #dict_plotdata['daily_meeting_time']['totalMeetingTime'] = dict_plotdata['daily_meeting_time']['totalMeetingTime'].apply(lambda x:x.days*24*60+x.seconds//60)#.to_dict(orient='split')
	    dict_plotdata['daily_meeting_time']['totalMeetingTime'] = dict_plotdata['daily_meeting_time']['totalMeetingTime'].apply(lambda x:float(x.days)*24+float(x.seconds)/3600)#.to_dict(orient='split')
	    #print dict_plotdata['daily_meeting_time']['totalMeetingTime']
	    #print dict_plotdata['daily_meeting_time']
	    
	    '''
            dict_plotdata['total_duration_of_meetings_min'] = np.sum(dict_plotdata['daily_meeting_time']['totalMeetingTime'])
            dict_plotdata['total_duration_of_meetings'] = str(dict_plotdata['total_duration_of_meetings_min']//60) + " hr " + str(dict_plotdata['total_duration_of_meetings_min']%60) + " min" if dict_plotdata['total_duration_of_meetings_min']>60 else str(dict_plotdata['total_duration_of_meetings_min']) + " min"
	    dict_plotdata['avg_speaking_time'] = dict_plotdata['total_speaking_time']*60/dict_plotdata['total_duration_of_meetings_min']
            '''

	    dict_plotdata['total_duration_of_meetings_min'] = np.sum(dict_plotdata['daily_meeting_time']['totalMeetingTime']*60)
            dict_plotdata['total_duration_of_meetings'] = str(int(dict_plotdata['total_duration_of_meetings_min']//60)) + " hr " + str(int(dict_plotdata['total_duration_of_meetings_min']%60)) + " min" if dict_plotdata['total_duration_of_meetings_min']>60 else str(int(dict_plotdata['total_duration_of_meetings_min'])) + " min"
	    dict_plotdata['avg_speaking_time'] = int(dict_plotdata['total_speaking_time']*60/dict_plotdata['total_duration_of_meetings_min'])

	    #print "\nTotal number of turns taken by day"
	    #print "\n",group_data.groupby([group_data['startTime'].apply(datetime2str)]).agg({"totalTurns": np.sum})#.to_dict(orient='split')
	    dict_plotdata['daily_turns_count'] = group_data.groupby(pd.Grouper(key='startTime',freq='1D')).agg({"totalTurns": np.sum})#.to_dict(orient='split')
	    dict_plotdata['daily_turns_rate'] = dict_plotdata['daily_turns_count']['totalTurns'].divide(dict_plotdata['daily_meeting_time']['totalMeetingTime']*60) #per minute
	    
            dict_plotdata['daily_meeting_time'] = dict_plotdata['daily_meeting_time'].reindex(idx, fill_value=0)
            #print dict_plotdata['daily_meeting_time']
            dict_plotdata['daily_turns_rate'] = dict_plotdata['daily_turns_rate'].reindex(idx, fill_value=0)
            #print dict_plotdata['daily_turns_rate']

	    #print "Number of turns taken per minute for the longest group meeting this week"
	    longest_meeting = group_data.loc[group_data['totalMeetingTime'].argmax()]['uuid']
	    group_meeting_data = groups_meeting_data[group_name]
	    for df in group_meeting_data:
	        if(df.metadata['uuid']==longest_meeting):
	            df_meeting=pd.pivot_table(df.reset_index(),index='datetime',columns='member',values='signal').fillna(value=0)
	            df_meeting.index = df_meeting.index - np.timedelta64(4, 'h') # Convert UTC to EST
                    #df_meeting.index = df_meeting.index.tz_localize('UTC').tz_convert('US/Eastern')
	            dict_plotdata['longest_meeting_date'] = pd.to_datetime(str(df_meeting.index.values[0])).strftime('%A %Y-%m-%d')
	            df_meeting_turns = get_speaking_series(df_meeting)
	            df_meeting_turns['total'] = df_meeting_turns.sum(axis=1)
	            break
	    dict_plotdata['longest_meeting_turns'] = df_meeting_turns['total']
	    
	    #print "Number of participants per meeting:"
	    #print group_data.groupby('uuid')['member'].count()
	    dict_plotdata['meeting_member_count'] = group_data.groupby('uuid')['member'].count()
	    dict_plotdata['avg. member count'] = np.mean(dict_plotdata['meeting_member_count'])


            #i += 1
            #print("3:"+str(i)+ group + " "+str(time.time()))    
            print("Data processed for "+group)
           
 
            ax1 = dict_plotdata['type_meeting_count']['meeting_count'].plot.pie(legend=True,labels=None,autopct='%.1f%%')
            ax1.set_aspect('equal')
            fig_type = ax1.get_figure()
            plt.ylabel('')
            plt.xlabel('')
            plt.setp(plt.gca().get_legend().get_texts(), fontsize='18')
            plt.tight_layout()
            mpld3.fig_to_html(fig_type)

            reports_path = settings.MEDIA_ROOT + "/img/weekly_group_reports/" + dict_plotdata['group_name']
            def make_sure_path_exists(path):
                try: 
                    os.makedirs(path)
                except OSError:
                    if not os.path.isdir(path):
                        raise
            make_sure_path_exists(reports_path)
            plt.savefig(reports_path + "/week_" + week_num + "_type_meeting_count.png")
            plt.gcf().clear()
            
            ax2 = dict_plotdata['location_meeting_count']['meeting_count'].plot.pie(legend=True,labels=None,autopct='%.1f%%')
            ax2.set_aspect('equal')
            fig_loc = ax2.get_figure()
            #plt.title('Meetings by location',fontsize=title_fontsize)
            plt.ylabel('')
            plt.xlabel('')
            plt.setp(plt.gca().get_legend().get_texts(), fontsize='18')
            plt.tight_layout()
            mpld3.fig_to_html(fig_loc)
            plt.savefig(reports_path + "/week_" + week_num + "_location_meeting_count.png")
            plt.gcf().clear()
	
            fig_meet_time, ax3 = plt.subplots(figsize=(scale*2.5, scale*1.5))
            ax3.xaxis.set_major_locator(DayLocator())
            ax3.xaxis.set_major_formatter(DateFormatter('%A'))
            ax3.bar(dict_plotdata['daily_meeting_time'].index, dict_plotdata['daily_meeting_time']['totalMeetingTime'],align="center")
            fig_meet_time.autofmt_xdate()
            plt.ylabel('Total meeting duration (hours)',fontsize=y_fontsize)
            #plt.xlabel('Day', fontsize=x_fontsize)
            plt.tight_layout()
            plt.savefig(reports_path + "/week_" + week_num + "_daily_meeting_time.png")
            plt.gcf().clear()
	
            fig_turns_count, ax5 = plt.subplots(figsize=(scale*2.5, scale*1.5))
            ax5.xaxis.set_major_locator(DayLocator())
            ax5.xaxis.set_major_formatter(DateFormatter('%A'))
            ax5.bar(dict_plotdata['daily_turns_rate'].index, dict_plotdata['daily_turns_rate'],align="center")
            fig_meet_time.autofmt_xdate()
            #plt.title('Number of speaking turns by day',fontsize=title_fontsize)
            plt.ylabel('Average number of speaking turns per hour',fontsize=y_fontsize)
            #plt.xlabel('Day', fontsize=x_fontsize)
            plt.tight_layout()
            mpld3.fig_to_html(fig_turns_count)
            plt.savefig(reports_path + "/week_" + week_num + "_daily_turns_rate.png")
            plt.gcf().clear()
            
            #minorLocator = HourLocator() #removed because hours labels didn't show on some graphs
            ax4 = dict_plotdata['longest_meeting_turns'].resample('S').interpolate(method='linear').rolling(window=60, min_periods=1, center=False).mean().plot(figsize=(scale*5,scale*2))
            #clip(lower=0.0).plot(figsize=(scale*5,scale*2))#
            #ax4.xaxis.set_minor_locator(minorLocator)
            fig_meet_turns = ax4.get_figure()
            #plt.title('Number of turns per minute in the longest meeting',fontsize=title_fontsize)
            plt.ylabel('Average number of turns taken', fontsize=y_fontsize+2)
            plt.xlabel('Time', fontsize=x_fontsize+2)
            plt.tight_layout()
            mpld3.fig_to_html(fig_meet_turns)
            plt.savefig(reports_path + "/week_" + week_num + "_longest_meeting_turns.png")
            plt.gcf().clear()

            WeeklyGroupReport.objects.filter(group_key=dict_plotdata['group_name'], week_num=week_num).delete()
            WeeklyGroupReport.objects.create(group_key=dict_plotdata['group_name'],
                                             week_num=week_num,
                                             start_date=start_date,
                                             end_date=end_date,
                                             total_meeting_count=dict_plotdata['total_meeting_count'],
                                             total_duration_of_meetings=dict_plotdata['total_duration_of_meetings'],
                                             avg_speaking_time=dict_plotdata['avg_speaking_time'],
                                             longest_meeting_date=dict_plotdata['longest_meeting_date']
            )
             
            print("Charts generated for "+group)
        
        print("End: "+str(time.time()))
        print("Successfully generated charts for all meetings for Week "+week_num+"!")
