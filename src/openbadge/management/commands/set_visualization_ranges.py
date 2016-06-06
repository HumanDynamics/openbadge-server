from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import set_visualization_ranges


class Command(BaseCommand):
    help = 'Set visualization ranges'

    def add_arguments(self, parser):
        parser.add_argument('--group_key', nargs=1, type=str)

    def handle(self, *args, **options):
        group_key = options["group_key"][0]
        num_groups = set_visualization_ranges(group_key)

        self.stdout.write("Updated {0} groups successfully!".format(num_groups))
