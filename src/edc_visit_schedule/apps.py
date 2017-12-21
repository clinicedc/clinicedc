import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_visit_schedule'
    verbose_name = "Visit Schedules"
    validate_models = True

    def ready(self):
        from .signals import offschedule_model_on_post_save
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_visit_schedules.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')


if settings.APP_NAME == 'edc_visit_schedule':

    from dateutil.relativedelta import MO, TU, WE, TH, FR
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            'default': dict(days=[MO, TU, WE, TH, FR],
                            slots=[100, 100, 100, 100, 100])}
