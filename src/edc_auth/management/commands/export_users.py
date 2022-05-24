from django.core.management.base import BaseCommand

from edc_auth.export_users import export_users


class Command(BaseCommand):

    help = "Export users to a CSV file in the current directory"

    def add_arguments(self, parser):
        parser.add_argument("--csvfile", default=None, dest="csvfile", help="CSV filename")

        parser.add_argument(
            "--verbose",
            default=False,
            action="store_true",
            dest="verbose",
            help="Verbose mode",
        )

        parser.add_argument(
            "--export",
            default=False,
            action="store_true",
            dest="export_to_file",
            help="Export new users to file",
        )

    def handle(self, *args, **options):

        export_users(options["csvfile"])
