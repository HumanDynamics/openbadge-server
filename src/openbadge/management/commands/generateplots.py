from django.core.management.base import BaseCommand, CommandError
from openbadge.views import data_process

class Command(BaseCommand):
    help = 'Generate charts and plots for weekly external reports'

    def add_arguments(self, parser):
        parser.add_argument('--start_date', nargs=1, type=str)
        parser.add_argument('--end_date', nargs=1, type=str)

    def handle(self, *args, **options):
        start_date = options["start_date"][0]
        end_date = options["end_date"][0]

        data_process(start_date, end_date)

        self.stdout.write("Successfully generated plots for all meetings from {0} to {1}!".format(start_date, end_date))
