import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.core.checks import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

from .site_visit_schedules import site_visit_schedules
from .system_checks import visit_schedule_check

style = color_style()


def populate_visit_schedule(sender=None, **kwargs):
    from .models import VisitSchedule

    sys.stdout.write(style.MIGRATE_HEADING("Populating visit schedule:\n"))
    VisitSchedule.objects.update(active=False)
    site_visit_schedules.to_model(VisitSchedule)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


class AppConfig(DjangoAppConfig):
    name = "edc_visit_schedule"
    verbose_name = "Visit Schedules"
    validate_models = True
    include_in_administration_section = True

    def ready(self):
        post_migrate.connect(populate_visit_schedule, sender=self)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_visit_schedules.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        register(visit_schedule_check)
