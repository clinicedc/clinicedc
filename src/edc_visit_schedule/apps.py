import sys

from django.apps.config import AppConfig
from django.core.management.color import color_style
# from django.db.models.signals import post_migrate
# from edc_content_type_map.apps import edc_content_type_callback

style = color_style()


def build_visit_schedules(sender, **kwargs):
    from edc_visit_schedule.site_visit_schedules import site_visit_schedules
    sys.stdout.write('Running post-migrate for {} ...\n'.format(sender.verbose_name))
    sys.stdout.write(' * update data in visit schedule models\n'.format(sender.verbose_name))
    site_visit_schedules.build_all()
    sys.stdout.write('{} done. \n'.format(sender.verbose_name))


class EdcVisitScheduleAppConfig(AppConfig):
    name = 'edc_visit_schedule'
    verbose_name = "Visit Schedule"
    model = None

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        from edc_visit_schedule.site_visit_schedules import site_visit_schedules
        site_visit_schedules.autodiscover()
        sys.stdout.write(' * update data in visit schedule models\n')
        site_visit_schedules.build_all()
        # post_migrate.connect(build_visit_schedules, sender=self)
        sys.stdout.write(' Done {}.\n'.format(self.verbose_name))
