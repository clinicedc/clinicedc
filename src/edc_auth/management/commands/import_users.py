from django.core.management.base import BaseCommand

from edc_auth.import_users import import_users


class Command(BaseCommand):
    help = "Import users from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csvfile", default="users.csv", dest="csvfile", help="CSV filename"
        )
        parser.add_argument(
            "--notify-to-test-email",
            default="",
            dest="notify_to_test_email",
            help="Email address to use when notifying users (for testing)",
        )

        parser.add_argument(
            "--resend-as-new",
            default=False,
            action="store_true",
            dest="resend_as_new",
            help="Send email to user as if newly created",
        )

        parser.add_argument(
            "--resource-name",
            type=str,
            default="clinicedc.org",
            dest="resource_name",
            help="Mail server domain",
        )

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

        parser.add_argument(
            "--notify-users",
            default=False,
            action="store_true",
            dest="notify_users",
            help="Send email to users",
        )

        parser.add_argument(
            "--limit_to_user",
            default="",
            type=str,
            dest="limit_to_username",
            help="Limit import to a single username",
        )

    def handle(self, *args, **options):
        import_users(
            options["csvfile"],
            resource_name=options["resource_name"],
            send_email_to_user=options["notify_users"],
            verbose=options["verbose"],
            export_to_file=options["export_to_file"],
            test_email_address=options["notify_to_test_email"],
            resend_as_new=options["resend_as_new"],
            limit_to_username=options["limit_to_username"],
        )
