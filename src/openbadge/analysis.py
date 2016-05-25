import smtplib, os, simplejson, datetime, csv, pytz
import time

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

from email.header import Header

from passwords import GMAIL_PASSWORD, GMAIL_USERNAME

from django.template import loader

from .models import StudyGroup, StudyMember
from django.conf import settings


def post_meeting_analysis(meeting):
    member_ids = simplejson.loads(meeting.members)
    members = meeting.group.members.filter(key__in=member_ids).all()
    recipients = [member.email for member in members]


    eastern = pytz.timezone('US/Eastern')
    start_time = meeting.start_time.astimezone(eastern)

    #TODO: do analysis
    chunks = meeting.get_chunks()
    total_samples = sum([sum(chunk["samples"]) for chunk in chunks])
    analysis_results = dict(total_samples=total_samples)

    template = loader.get_template("email/end_meeting_email.html")

    for member in members:
        body = template.render(dict(meeting=meeting, analysis_results=analysis_results, start_time=start_time, member_key=member.key))
        send_email(GMAIL_USERNAME, GMAIL_PASSWORD, member.email, "OpenBadge Post-Meeting Analysis", body)
        time.sleep(.3)


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
        send_email(GMAIL_USERNAME, GMAIL_PASSWORD, recipient, "OpenBadge Weekly Analysis", body)
        time.sleep(.3)


def send_email(user, pwd, recipient, subject, body):

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = [recipient]

    msg = MIMEMultipart("", _charset="UTF-8")

    msg['FROM'] = FROM
    msg['To'] = recipient
    msg['Subject'] = Header(subject, "utf-8")

    msg.attach(MIMEText(body, 'html', 'UTF-8'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
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

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            # only create new users if we don't have one with the same email
            if row['email'] not in members.keys():

                # create a new group for the member if we don't have one already
                if row['group'] not in groups.keys():
                    group = StudyGroup(name=row['group'])
                    group.save()
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

    return num_new_members, num_new_groups

