from dateutil.relativedelta import relativedelta

from edc_consent.consent_definition import ConsentDefinition
from edc_protocol.research_protocol_config import ResearchProtocolConfig

# default consent definition for most tests
consent_v1 = ConsentDefinition(
    "tests.subjectconsentv1",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="1",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)

consent1_v1 = ConsentDefinition(
    "tests.subjectconsentv1",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_open_datetime + relativedelta(days=50),
    gender=["M", "F"],
    version="1.0",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)


consent1_v2 = ConsentDefinition(
    "tests.subjectconsentv2",
    start=ResearchProtocolConfig().study_open_datetime + relativedelta(days=51),
    end=ResearchProtocolConfig().study_open_datetime + relativedelta(days=100),
    gender=["M", "F"],
    version="2.0",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)

consent1_v3 = ConsentDefinition(
    "tests.subjectconsentv3",
    start=ResearchProtocolConfig().study_open_datetime + relativedelta(days=101),
    end=ResearchProtocolConfig().study_open_datetime + relativedelta(days=200),
    gender=["M", "F"],
    version="3.0",
    age_min=16,
    age_max=64,
    age_is_adult=18,
    updates=consent1_v2,
)


consent2_v1 = ConsentDefinition(
    "tests.subjectconsent2v1",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="2.1",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)

consent2_v2 = ConsentDefinition(
    "tests.subjectconsent2v2",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="2.2",
    age_min=16,
    age_max=64,
    age_is_adult=18,
    updates=consent2_v1,
)

consent5_v1 = ConsentDefinition(
    "tests.subjectconsentv5",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="5",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)

consent6_v1 = ConsentDefinition(
    "tests.subjectconsentv6",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="6",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)

consent7_v1 = ConsentDefinition(
    "tests.subjectconsentv7",
    start=ResearchProtocolConfig().study_open_datetime,
    end=ResearchProtocolConfig().study_close_datetime,
    gender=["M", "F"],
    version="7",
    age_min=16,
    age_max=64,
    age_is_adult=18,
)
