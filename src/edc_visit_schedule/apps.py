import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_visit_schedule'
    verbose_name = "Visit Schedules"
    validate_models = True

    def ready(self):
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_visit_schedules.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
