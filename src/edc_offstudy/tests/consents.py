from django.apps import apps as django_apps
from edc_constants.constants import MALE, FEMALE
from edc_consent.consent import Consent

edc_protocol = django_apps.get_app_config('edc_protocol')

v1_consent = Consent(
    'edc_appointment.subjectconsent',
    version='1',
    start=edc_protocol.study_open_datetime,
    end=edc_protocol.study_close_datetime,
    age_min=18,
    age_is_adult=18,
    age_max=64,
    gender=[MALE, FEMALE])
