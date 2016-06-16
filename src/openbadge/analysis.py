import smtplib, os, simplejson, datetime, csv, pytz
import time

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

from email.header import Header

import passwords

from django.template import loader

from .models import StudyGroup, StudyMember, VisualizationRange
from django.conf import settings
import urllib

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


def send_weekly_email(group):

    members = group.members.all()
    recipients = [member.email for member in members]

    start_time = datetime.datetime.now() - datetime.timedelta(days=7)

    meetings = group.meetings.filter(start_time__gte=start_time)

    #TODO: do analysis
    for meeting in meetings:
        chunks = meeting.get_chunks()
    analysis_results = dict(total_meetings=len(meetings))

    template = loader.get_template("email/weekly_report_email.html")
    body = template.render(dict(group=group, analysis_results=analysis_results))

    for recipient in recipients:
        send_email(passwords.EMAIL_USERNAME, passwords.EMAIL_PASSWORD, recipient, "OpenBadge Weekly Analysis", body)
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
