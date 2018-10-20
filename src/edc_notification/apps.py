import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .site_notifications import site_notifications

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_notification'
    verbose_name = 'Edc Notification'

    def ready(self):
        from .signals import notification_on_post_save
        from .signals import manage_mailists_on_userprofile_m2m_changed
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_notifications.autodiscover(verbose=True)
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
