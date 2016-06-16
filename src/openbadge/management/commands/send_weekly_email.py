from django.core.management.base import BaseCommand, CommandError
import simplejson
from openbadge.analysis import send_weekly_email
from openbadge.models import StudyGroup

class Command(BaseCommand):
    help = 'Send the weekly email to a specified group (or all groups) for a specified week'

    def add_arguments(self, parser):
        parser.add_argument('--week_num', nargs=1, type=str)
        parser.add_argument('--group_key', nargs=1, type=str)

    def handle(self, *args, **options):
        week_num = options['week_num'][0]
        group_key = options['group_key'][0]

        # validate existance of group
        if group_key == "ALL":
            groups = StudyGroups.objects.all()
            for group in group:
                send_weekly_email(group, week_num)
        else:
            group = StudyGroup.objects.get(key=group_key)
            send_weekly_email(group, week_num)

        self.stdout.write("Sent the emails successfully!")




