from django.apps import apps as django_apps
from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents
from edc_constants.constants import MALE, FEMALE


edc_protocol = django_apps.get_app_config("edc_protocol")

v1 = Consent(
    "dashboard_app.subjectconsent",
    version="1",
    start=edc_protocol.study_open_datetime,
    end=edc_protocol.study_close_datetime,
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
)

site_consents.register(v1)
