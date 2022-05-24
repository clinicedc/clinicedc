import sys

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from edc_auth.password_setter import PasswordSetter


class Command(BaseCommand):

    help = "Reset a user's password"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("super_user")
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
            p = PasswordSetter(super_username=options["super_user"])
            p.reset_user(username=options["username"])
            sys.stdout.write(f"\nYour password has been reset and emailed to {user.email}\n")
