from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import set_members_timestamps
from decimal import *
import time

class Command(BaseCommand):
    help = 'Sets timestamps for all members of the given project key. ' \

    def add_arguments(self, parser):
        parser.add_argument('--project_key', nargs=1, type=str)

        parser.add_argument('--timestamp', nargs=1, type=str, help='Timestamp to set (optional)',)

    def handle(self, *args, **options):
        project_key = options["project_key"][0]

        if options["timestamp"]:
            init_timestamp = Decimal(options["timestamp"][0])
        else:
            init_timestamp = Decimal(int(time.time()))

        print(type(init_timestamp))
        self.stdout.write("Setting timestamp to: {0}".format(init_timestamp))
        if project_key is not None:
            num_members = set_members_timestamps(project_key, init_timestamp)
            self.stdout.write("Set timestamps for {0} members successfully!".format(num_members))

        else:
            self.stdout.write("Wrong parameters")

