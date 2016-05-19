from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import load_users_from_csv


class Command(BaseCommand):
    help = 'Import Study Members from a properly formatted CSV'

    def add_arguments(self, parser):
        parser.add_argument('--filename', nargs=1, type=str)

    def handle(self, *args, **options):
        filename = options["filename"][0]
        num_members, num_groups = load_users_from_csv(filename)

        self.stdout.write("Imported {0} new members and {1} new groups successfully!".format(num_members, num_groups))
