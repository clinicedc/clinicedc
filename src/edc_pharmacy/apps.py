import os

from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = "edc_pharmacy"
    verbose_name = "Pharmacy"
    prescription_model = "edc_pharmacy.prescription"
    worklist_model = "edc_pharmacy.worklist"
    template_name = None

    @property
    def study_site_name(self):
        return "Gaborone"

    @property
    def site_code(self):
        return "40"

    @property
    def facility(self):
        return self.facilities.get(self.country).get(self.map_area)


if settings.APP_NAME == "edc_pharmacy":
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        appointment_model = "edc_pharmacy.appointment"
