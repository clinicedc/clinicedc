from django.apps.config import AppConfig
from django.core.management.color import color_style
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

style = color_style()


class EdcVisitScheduleAppConfig(AppConfig):
    name = 'edc_visit_schedule'
    verbose_name = "Visit Schedule"
    model = None

    def ready(self):
        site_visit_schedules.autodiscover()
#         sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
#         from edc_visit_schedule.site_visit_schedules import site_visit_schedules
#         site_visit_schedules.autodiscover()
#         post_migrate.connect(build_visit_schedules, sender=self)
#         sys.stdout.write(' Done {}.\n'.format(self.verbose_name))
