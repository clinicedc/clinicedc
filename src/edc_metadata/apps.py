import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT


style = color_style()

subject_visit_model = getattr(
    settings, "SUBJECT_VISIT_MODEL", "edc_metadata.subjectvisit"
)


class AppConfig(DjangoAppConfig):
    name = "edc_metadata"
    verbose_name = "Edc Metadata"
    has_exportable_data = True
    reason_field = {subject_visit_model: "reason"}
    create_on_reasons = [SCHEDULED, UNSCHEDULED]
    delete_on_reasons = [MISSED_VISIT]
    include_in_administration_section = True

    def ready(self):
        from .signals import (
            metadata_update_on_post_save,  # noqa
            metadata_create_on_post_save,  # noqa
            metadata_reset_on_post_delete,  # noqa
        )

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")


if settings.APP_NAME == "edc_metadata":

    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {"edc_metadata": ("subject_visit", "edc_metadata.subjectvisit")}

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(
                days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
            ),
        }
