import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_metadata"
    verbose_name = "Edc Metadata"
    has_exportable_data = True
    reason_field = {settings.SUBJECT_VISIT_MODEL: "reason"}
    create_on_reasons = [SCHEDULED, UNSCHEDULED, MISSED_VISIT]
    delete_on_reasons = []
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
