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
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_visit_schedules.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
