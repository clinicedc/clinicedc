from django.core.management.base import BaseCommand

from edc_notification.site_notifications import site_notifications


class Command(BaseCommand):
    help = "List email recipients for each registered notification"

    def handle(self, *args, **options):
        for notification_cls in site_notifications.registry.values():
            notification = notification_cls()
            print()
            print(notification.name)
            print(notification.display_name)
            print(f"email: {notification.email_to}")
