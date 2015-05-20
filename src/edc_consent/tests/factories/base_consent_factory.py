import factory
from datetime import datetime
from edc.core.bhp_variables.tests.factories import StudySiteFactory
from .base_consent_basics_factory import BaseConsentBasicsFactory


class BaseConsentFactory(BaseConsentBasicsFactory):
    ABSTRACT_FACTORY = True

    study_site = factory.SubFactory(StudySiteFactory)
    consent_datetime = datetime.today()
    may_store_samples = 'Yes'
    is_incarcerated = 'No'
