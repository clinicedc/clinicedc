import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.core.checks.registry import register
from django.db.models.signals import post_migrate

from .system_checks import edc_notification_check
from .site_notifications import site_notifications

style = color_style()


def post_migrate_update_notifications(sender=None, **kwargs):
    site_notifications.update_notification_list(verbose=True)
    site_notifications.create_mailing_lists(verbose=True)


class AppConfig(DjangoAppConfig):
    name = "edc_notification"
    verbose_name = "Edc Notification"
    include_in_administration_section = True

    def ready(self):
        from .signals import manage_mailists_on_userprofile_m2m_changed  # noqa
        from .signals import notification_on_post_create_historical_record  # noqa

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_notifications.autodiscover(verbose=True)
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        post_migrate.connect(post_migrate_update_notifications, sender=self)
        register(edc_notification_check)
