from django.apps import AppConfig
from django.apps import apps as django_apps

from django_crypto_fields.apps import DjangoCryptoFieldsAppConfig as DjangoCryptoFieldsAppConfigParent

from edc_meta_data.apps import EdcMetaDataAppConfig as EdcMetaDataAppConfigParent


class EdcAppointmentAppConfig(AppConfig):
    name = 'edc_appointment'
    verbose_name = "EDC Appointments"
    model = ('example', 'appointment')
    institution = 'Botswana Harvard Partnership'
    appointments_days_forward = 0
    appointments_per_day_max = 30
    use_same_weekday = True
    weekday = 2
    allowed_iso_weekdays = '12345'
    default_appt_type = 'clinic'

    @property
    def appointment_model(self):
        return django_apps.get_model(*self.model)


class EdcMetaDataAppConfig(EdcMetaDataAppConfigParent):
    model_attrs = [('example', 'crfmetadata'), ('example', 'requisitionmetadata')]


class DjangoCryptoFieldsAppConfig(DjangoCryptoFieldsAppConfigParent):
    model = ('example', 'crypt')
    crypt_model_using = 'default'
