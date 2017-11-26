from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from edc_timepoint.timepoint_collection import TimepointCollection
from edc_timepoint.timepoint import Timepoint
from edc_appointment.constants import COMPLETE_APPT
from edc_timepoint.apps import AppConfig as BaseEdcTimepointAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_subject_dashboard'


if settings.APP_NAME == 'edc_subject_dashboard':

    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_appointment.appointment_config import AppointmentConfig

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):

        configurations = [
            AppointmentConfig(
                model='edc_subject_dashboard.appointment',
                related_visit_model='edc_subject_dashboard.subjectvisit')
        ]

    class EdcTimepointAppConfig(BaseEdcTimepointAppConfig):

        timepoints = TimepointCollection(
            timepoints=[
                Timepoint(
                    model='edc_subject_dashboard.appointment',
                    datetime_field='appt_datetime',
                    status_field='appt_status',
                    closed_status=COMPLETE_APPT),
            ])
