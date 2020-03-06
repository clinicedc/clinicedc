from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents
from edc_constants.constants import MALE, FEMALE
from edc_protocol import Protocol

v1 = Consent(
    "edc_model_admin.subjectconsent",
    version="1",
    start=Protocol().study_open_datetime,
    end=Protocol().study_close_datetime,
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
)

site_consents.register(v1)
