import simplejson, datetime
from decimal import Decimal

from django.test import TestCase, Client
from django.conf import settings

from django.db import transaction

from rest_framework_expiring_authtoken.models import ExpiringToken

from .models import StudyGroup, StudyMember, Meeting, VisualizationRange
import analysis

class APITest(TestCase):

    def setUp(self):
        # setup group, members, meeting
        StudyGroup.objects.create(name="Oren group")
        group = StudyGroup.objects.get(name="Oren group")

        StudyMember.objects.create(name="Oren Lederman", email = "orenled@mit.edu", badge="AA:AA:AA:AA", group = group)
        StudyMember.objects.create(name="Alice", email="badgeB@or3n.com", badge="AA:AA:AA:AA", group=group)
        member1 = StudyMember.objects.get(name="Oren Lederman")
        member2 = StudyMember.objects.get(name="Alice")

        memberKeys = [member1.key,member2.key]
        meetingMembers = simplejson.dumps(memberKeys)

        VisualizationRange.objects.create(group=group,start=datetime.datetime.now(),end=datetime.datetime.now())


        # Generate a meeting
        # Generate a dummy logfile
        LOG_FILE_TEXT = """logloglog
        loglogloglog
        loglogloglog"""

        LOG_FILE_NAME = settings.MEDIA_ROOT+'/logs/test_file.txt';
        text_file = open(LOG_FILE_NAME, "w")
        text_file.write(LOG_FILE_TEXT)
        text_file.close()

        Meeting.objects.create(\
            group = group, uuid="fakeid",type="fake_type",location="fake_location",description="fake description"\
            ,is_complete=True,show_visualization=True,start_time=datetime.datetime.now(),end_time=datetime.datetime.now()\
            ,members=meetingMembers,log_file=LOG_FILE_NAME
            )

    def test_group_created(self):
        group = StudyGroup.objects.get(name="Oren group")
        members = group.members.all()
        self.assertEqual(group.name,"Oren group")
        names = [member.name for member in members]
        meetings = meetings = group.meetings.all()

    def test_group_send_survey(self):
        group = StudyGroup.objects.get(name="Oren group")
        meetings = group.meetings.all()
        meeting = meetings[0]
        analysis.post_meeting_analysis(meeting)


    def test_weekly_email(self):
        group = StudyGroup.objects.get(name="Oren group")
        analysis.send_weekly_email(group,'2')