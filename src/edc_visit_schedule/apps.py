import sys

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz.tz import gettz
from django.apps.config import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks import register
from django.core.management.color import color_style
from edc_utils import get_utcnow
from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig

from .site_visit_schedules import site_visit_schedules
from .system_checks import visit_schedule_check

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_visit_schedule"
    verbose_name = "Visit Schedules"
    validate_models = True

    def ready(self):
        from .signals import (
            offschedule_model_on_post_save,
            onschedule_model_on_post_save,
        )

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_visit_schedules.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        register(visit_schedule_check)


if settings.APP_NAME == "edc_visit_schedule":

    from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        configurations = []

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            "default": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
                best_effort_available_datetime=True,
            )
        }

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {
            "edc_visit_schedule": ("subject_visit", "edc_visit_schedule.subjectvisit")
        }

    class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
        protocol = "BHP099"
        protocol_number = "099"
        protocol_name = "TestApp"
        protocol_title = ""
        study_open_datetime = datetime(2007, 12, 31, 0, 0, 0, tzinfo=gettz("UTC"))
        study_close_datetime = get_utcnow() + relativedelta(years=5)

        @property
        def site_name(self):
            return "Gaborone"
