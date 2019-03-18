from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from edc_appointment.appointment_config import AppointmentConfig


class AppConfig(DjangoAppConfig):
    name = "edc_model_admin"


if settings.APP_NAME == "edc_model_admin":

    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {
            "edc_model_admin": ("subject_visit", "edc_model_admin.subjectvisit")
        }

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

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        configurations = [
            AppointmentConfig(
                model="edc_appointment.appointment",
                related_visit_model="edc_model_admin.subjectvisit",
                appt_type="hospital",
            )
        ]

    class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):
        reason_field = {"edc_model_admin.subjectvisit": "reason"}
