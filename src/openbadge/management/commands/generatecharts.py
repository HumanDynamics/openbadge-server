from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import data_process

class Command(BaseCommand):
    help = 'Generate charts and plots for weekly external reports'

    def add_arguments(self, parser):
        parser.add_argument('--week_num', nargs=1, type=str)

    def handle(self, *args, **options):
        week_num = options["week_num"][0]

        data_process(week_num)

        self.stdout.write("Successfully generated charts for all meetings for Week {0}!".format(week_num))
