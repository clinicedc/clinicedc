from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = "edc_subject_dashboard"


if settings.APP_NAME == "edc_subject_dashboard":

    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_appointment.appointment_config import AppointmentConfig

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):

        configurations = [
            AppointmentConfig(
                model="edc_appointment.appointment",
                related_visit_model="edc_subject_dashboard.subjectvisit",
            )
        ]
