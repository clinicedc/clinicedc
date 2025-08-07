from datetime import datetime
from zoneinfo import ZoneInfo

from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_protocol.research_protocol_config import ResearchProtocolConfig

consent_v1 = ConsentDefinition(
    proxy_model="demo_consent.subjectconsentv1",
    version="1",
    start=ResearchProtocolConfig().study_open_datetime,
    end=datetime(2024, 4, 22, 13, 59, 59, tzinfo=ZoneInfo("UTC")),
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
    screening_model=["demo_screening.subjectscreening"],
)

consent_v2 = ConsentDefinition(
    proxy_model="demo_consent.subjectconsentv2",
    version="2",
    start=datetime(2024, 4, 22, 14, 0, 0, tzinfo=ZoneInfo("UTC")),
    end=ResearchProtocolConfig().study_close_datetime,
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
    screening_model=["demo_screening.subjectscreening"],
    updates=consent_v1,
)

site_consents.register(consent_v1, updated_by=consent_v2)
site_consents.register(consent_v2)
