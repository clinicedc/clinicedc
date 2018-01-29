import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class EdcOffstudyAppConfigError(Exception):
    pass


ATTR = 0
MODEL_LABEL = 1


class AppConfig(DjangoAppConfig):
    name = 'edc_offstudy'
    verbose_name = 'Edc Offstudy'

    def ready(self):
        from .signals import offstudy_model_on_post_save
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        # sys.stdout.write('  * using offstudy models from \'{}\'\n'.format(self.app_label))
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))


if settings.APP_NAME == 'edc_offstudy':

    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_appointment.appointment_config import AppointmentConfig
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {
            'edc_offstudy': ('subject_visit', 'edc_offstudy.subjectvisit')}

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        configurations = [
            AppointmentConfig(
                model='edc_appointment.appointment',
                related_visit_model='edc_offstudy.subjectvisit')]

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            'default': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                            slots=[100, 100, 100, 100, 100])}
