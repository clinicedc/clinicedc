from django.apps.config import AppConfig


class EdcVisitScheduleAppConfig(AppConfig):
    name = 'edc_visit_schedule'
    verbose_name = "Visit Schedule"
    model = None

    def ready(self):
        from edc_visit_schedule.site_visit_schedules import site_visit_schedules
        site_visit_schedules.autodiscover()
