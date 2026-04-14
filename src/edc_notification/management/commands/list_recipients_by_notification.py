import sys

from django.core.management.base import BaseCommand

from edc_notification.site_notifications import site_notifications


class Command(BaseCommand):
    help = "List email recipients for each registered notification"

    def handle(self, *args, **options):  # noqa: ARG002
        for notification_cls in site_notifications.registry.values():
            notification = notification_cls()
            sys.stdout.write(f"\n{notification.name}\n")
            sys.stdout.write(f"{notification.display_name}\n")
            sys.stdout.write(f"{notification.email_to}\n")
