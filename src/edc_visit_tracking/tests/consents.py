from edc_consent.consent_definition import ConsentDefinition
from edc_protocol import Protocol

consent_v1 = ConsentDefinition(
    model="edc_visit_tracking.subjectconsent",
    start=Protocol().study_open_datetime,
    end=Protocol().study_close_datetime,
    gender=["M", "F"],
    updates_versions=[],
    version="1",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)
