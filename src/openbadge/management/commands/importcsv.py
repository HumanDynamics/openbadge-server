from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import load_users_from_csv
from openbadge.analysis import set_visualization_ranges

class Command(BaseCommand):
    help = 'Import Study Members from a properly formatted CSV. Also sets visualization ranges for new gorups if provided'

    def add_arguments(self, parser):
        parser.add_argument('--filename', nargs=1, type=str)
        parser.add_argument('--ranges_filename', nargs=1, type=str)

    def handle(self, *args, **options):
        filename = options["filename"][0]
        if options["ranges_filename"]:
            ranges_filename = options["ranges_filename"][0]

        num_members, num_groups, new_group_keys = load_users_from_csv(filename)

        self.stdout.write("Imported {0} new members and {1} new groups successfully!".format(num_members, num_groups))

        if ranges_filename:
            for group_key in new_group_keys:
                self.stdout.write(
                    "Setting visualization ranges for {0}".format(group_key))
                num_vrs = set_visualization_ranges(group_key, ranges_filename)
