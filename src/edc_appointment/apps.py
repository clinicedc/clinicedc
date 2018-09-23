import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings

from .appointment_config import AppointmentConfig


class EdcAppointmentAppConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):

    _holidays = {}
    name = 'edc_appointment'
    verbose_name = "Edc Appointments"
    configurations = [
        AppointmentConfig(
            model='edc_appointment.appointment',
            related_visit_model='edc_appointment.subjectvisit')]
    has_exportable_data = True

    def ready(self):
        from .signals import (
            create_appointments_on_post_save,
            appointment_post_save,
            delete_appointments_on_post_delete)

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        for config in self.configurations:
            sys.stdout.write(f' * {config.name}.\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    def get_configuration(self, name=None, related_visit_model=None):
        """Returns an AppointmentConfig instance for the given
        name or related_visit_model.
        """
        if related_visit_model:
            attr, value = 'related_visit_model', related_visit_model
        else:
            attr, value = 'name', name
        try:
            appointment_config = [
                c for c in self.configurations if getattr(c, attr) == value][0]
        except IndexError:
            keys = [(c.name, c.related_visit_model)
                    for c in self.configurations]
            raise EdcAppointmentAppConfigError(
                f'AppointmentConfig not found. Got {name or related_visit_model}. '
                f'Expected one of {keys}. See edc_appointment.AppConfig "configurations".')
        return appointment_config


if settings.APP_NAME == 'edc_appointment':

    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            '7-day-clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                                 slots=[100, 100, 100, 100, 100, 100, 100]),
            '5-day-clinic': dict(days=[MO, TU, WE, TH, FR],
                                 slots=[100, 100, 100, 100, 100]),
            '3-day-clinic': dict(days=[TU, WE, TH],
                                 slots=[100, 100, 100],
                                 best_effort_available_datetime=True)}
