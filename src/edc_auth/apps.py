import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_auth'
    verbose_name = 'Edc Authentication'

    def ready(self):
        from .signals import update_user_profile_on_post_save  # noqa
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
