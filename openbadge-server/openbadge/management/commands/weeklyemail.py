from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import send_weekly_email
from openbadge.models import StudyGroup

class Command(BaseCommand):
    help = 'Send the weekly email to all members of a group, or all groups if no key is provided'

    def add_arguments(self, parser):
        parser.add_argument('--group_id', nargs='*', type=str)

    def handle(self, *args, **options):
        group_ids = options['group_id']
        if group_ids:
            groups = StudyGroup.objects.filter(key__in=group_ids).all()
        else:
            groups = StudyGroup.objects.all()

        for group in groups:
            send_weekly_email(group)
            self.stdout.write("Sent emails to group {0}".format(group.key))

        self.stdout.write("Sent all the emails successfully!")
