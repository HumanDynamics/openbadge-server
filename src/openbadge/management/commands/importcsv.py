from django.core.management.base import BaseCommand, CommandError
from openbadge.analysis import load_users_from_csv

class Command(BaseCommand):
    help = 'Import members from a properly formatted CSV to the given project key. ' \
           'Users are identified by email addresses. Format:\n' \
           'email, group, name, badge\n' \
           'Where "badge" is the MAC address, and "group" isn\'t currently used'

    def add_arguments(self, parser):
        parser.add_argument('--project_key', nargs=1, type=str)

        parser.add_argument('--filename', nargs=1, type=str)

    def handle(self, *args, **options):
        project_key = options["project_key"][0]
        filename = options["filename"][0]

        if (project_key is not None) and (filename is not None):
            num_members = load_users_from_csv(project_key, filename)
            self.stdout.write("Imported {0} new members successfully!".format(num_members))

        else:
            self.stdout.write("Wrong parameters")

