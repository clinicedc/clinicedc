from edc_consent.consent_definition import ConsentDefinition
from edc_protocol.research_protocol_config import ResearchProtocolConfig

consent_v1 = ConsentDefinition(
    model="edc_visit_tracking.subjectconsent",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    updates_versions=[],
    version="1",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)
