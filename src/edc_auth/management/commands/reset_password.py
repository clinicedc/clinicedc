import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from edc_auth.password_setter import PasswordSetter


class Command(BaseCommand):

    help = "Reset a user's password"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument(
            "--resource",
            default="clinicedc.org",
            action="store_true",
            dest="resource",
            help="Resource name",
        )

        parser.add_argument(
            "--email", action="store_true", dest="email", help="Alternate email"
        )

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options["username"])
        except ObjectDoesNotExist as e:
            raise CommandError(e)
        else:
            p = PasswordSetter()
            p.reset_user(
                resource_name=options["resource"], username=options["username"]
            )
            sys.stdout.write(
                f"\nYour password has been reset and " f"emailed to {user.email}\n"
            )
