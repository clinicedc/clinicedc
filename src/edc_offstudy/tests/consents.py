from clinicedc_constants import FEMALE, MALE

from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_protocol.trial_dates import trial_dates

consent_v1 = ConsentDefinition(
    "edc_offstudy.subjectconsentv1",
    version="1",
    start=trial_dates.study_open_datetime,
    end=trial_dates.study_close_datetime,
    age_min=18,
    age_is_adult=18,
    age_max=64,
    gender=[MALE, FEMALE],
)

site_consents.register(consent_v1)
