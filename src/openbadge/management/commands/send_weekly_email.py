from django.core.management.base import BaseCommand, CommandError
import simplejson
from openbadge.analysis import send_weekly_email
from openbadge.models import StudyGroup

class Command(BaseCommand):
    help = 'Send the weekly email to a specified group (or all groups) for a specified week'

    def add_arguments(self, parser):
        parser.add_argument('--week_num', nargs=1, type=str)
        parser.add_argument('--group_keys', nargs="*", type=str)

    def handle(self, *args, **options):
        week_num = options['week_num'][0]
        group_keys = options['group_keys']

        if group_keys:
            groups = StudyGroup.objects.filter(key__in=group_keys).all()
        else:
            groups = StudyGroup.objects.all()
        
        for group in groups:
            self.stdout.write("Sending emails to group {0}".format(group.key))
            send_weekly_email(group, week_num)

        self.stdout.write("Sent the emails successfully!")




