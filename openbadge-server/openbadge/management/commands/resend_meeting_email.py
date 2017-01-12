from django.core.management.base import BaseCommand, CommandError
import simplejson
from openbadge.analysis import send_post_meeting_survey
from openbadge.models import StudyMember, Meeting

class Command(BaseCommand):
    help = 'Send the post-meeting email email to a given member'

    def add_arguments(self, parser):
        parser.add_argument('--meeting_uuid', nargs=1, type=str)
        parser.add_argument('--member_key', nargs=1, type=str)

    def handle(self, *args, **options):
        meeting_uuid = options['meeting_uuid'][0]
        member_key = options['member_key'][0]

        # validate existance of meeting and member
        meeting = Meeting.objects.get(uuid=meeting_uuid)
        member = StudyMember.objects.get(key=member_key)

        # validate member was part of the meeting
        member_ids = simplejson.loads(meeting.members)
        if member_key in member_ids:
            send_post_meeting_survey(meeting,member)
            self.stdout.write("Sent the email successfully!")
        else:
            self.stdout.write("Member was not in the meeting!")




