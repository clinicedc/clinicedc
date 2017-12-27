from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

from ..field_mixins import ReviewFieldsMixin, PersonalFieldsMixin, CitizenFieldsMixin
from ..field_mixins import VulnerabilityFieldsMixin, IdentityFieldsMixin
from ..model_mixins import ConsentModelMixin, RequiresConsentNonCrfModelMixin


class SubjectConsent(ConsentModelMixin, NonUniqueSubjectIdentifierModelMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     IdentityFieldsMixin, ReviewFieldsMixin, PersonalFieldsMixin,
                     CitizenFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectConsent2(ConsentModelMixin, NonUniqueSubjectIdentifierModelMixin,
                      UpdatesOrCreatesRegistrationModelMixin,
                      IdentityFieldsMixin, ReviewFieldsMixin, PersonalFieldsMixin,
                      CitizenFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    class Meta(ConsentModelMixin.Meta):
        pass


class TestModel(NonUniqueSubjectIdentifierModelMixin,
                RequiresConsentNonCrfModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta:
        consent_model = 'edc_consent.subjectconsent'
