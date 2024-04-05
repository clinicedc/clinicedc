import socket
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites

style = color_style()


class Command(BaseCommand):
    help = "Add / Update django Site model after changes to edc_sites"

    def add_arguments(self, parser):

        parser.add_argument(
            "--ping-hosts",
            default=False,
            action="store_true",
            dest="ping_hosts",
            help="Try to ping hosts",
        )

        parser.add_argument(
            "--suggest-hosts",
            default=False,
            action="store_true",
            dest="suggest_hosts",
            help="Suggest ALLOWED_HOSTS",
        )

    def handle(self, *args, **options) -> None:
        sys.stdout.write("\n\n")
        sys.stdout.write(" Edc Sites : Adding / Updating sites ...     \n")
        add_or_update_django_sites(verbose=True)
        if (
            "multisite" in settings.INSTALLED_APPS
            or "multisite.apps.AppConfig" in settings.INSTALLED_APPS
        ):
            from multisite.models import Alias
            from multisite.utils import create_or_sync_canonical_from_all_sites

            sys.stdout.write("\n Multisite. \n")
            create_or_sync_canonical_from_all_sites(verbose=True)

            sys.stdout.write("    multisite.Alias \n")
            for obj in Alias.objects.all():
                sys.stdout.write(
                    f"      - Site model: {obj.site.id}: {obj.domain} "
                    f"is_canonical={obj.is_canonical}.\n"
                )
        arg = [arg for arg in sys.argv if arg.startswith("--settings")]
        sys.stdout.write(f"\n Settings: reading from {arg}")
        sys.stdout.write("\n\n Current value of settings.ALLOWED_HOSTS\n")
        sys.stdout.write(style.WARNING(f"\n    DEBUG = {settings.DEBUG}\n"))
        sys.stdout.write("    ALLOWED_HOSTS = [\n")
        for host in settings.ALLOWED_HOSTS:
            sys.stdout.write(f"      {host},\n")
        sys.stdout.write("    ]\n")
        sys.stdout.write("\n Suggested settings.ALLOWED_HOSTS\n\n")
        sys.stdout.write("    ALLOWED_HOSTS = [\n")
        for single_site in site_sites.all(aslist=True):
            sys.stdout.write(f"      {single_site.domain},\n")
        sys.stdout.write("    ]\n")
        if options.get("ping_hosts"):
            sys.stdout.write("\n Looking up hosts:\n")
            for single_site in site_sites.all(aslist=True):
                try:
                    host = socket.gethostbyname(single_site.domain)
                except socket.gaierror as e:
                    sys.stdout.write(
                        style.ERROR(f"  {single_site.domain}: <not found>. Got {e}\n")
                    )
                else:
                    sys.stdout.write(f"  {single_site.domain}: {host} {style.SUCCESS('OK')}\n")
        sys.stdout.write("Done     \n")
