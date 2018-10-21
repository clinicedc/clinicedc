import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site_notifications import site_notifications

style = color_style()


def post_migrate_update_notifications(sender=None, **kwargs):
    from .update_notification_list import update_notification_list
    update_notification_list(apps=django_apps)


class AppConfig(DjangoAppConfig):
    name = 'edc_notification'
    verbose_name = 'Edc Notification'

    def ready(self):
        from .signals import manage_mailists_on_userprofile_m2m_changed
        from .signals import notification_on_post_create_historical_record
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_notifications.autodiscover(verbose=True)
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
        post_migrate.connect(post_migrate_update_notifications, sender=self)
