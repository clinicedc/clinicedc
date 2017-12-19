from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

from ..field_mixins import ReviewFieldsMixin, PersonalFieldsMixin, CitizenFieldsMixin
from ..field_mixins import VulnerabilityFieldsMixin
from ..field_mixins.bw import IdentityFieldsMixin
from ..model_mixins import ConsentModelMixin, RequiresConsentModelMixin


class SubjectConsent(ConsentModelMixin, NonUniqueSubjectIdentifierModelMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     IdentityFieldsMixin, ReviewFieldsMixin, PersonalFieldsMixin,
                     CitizenFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    class Meta(ConsentModelMixin.Meta):
        unique_together = ['subject_identifier', 'version']


class SubjectConsent2(ConsentModelMixin, NonUniqueSubjectIdentifierModelMixin,
                      UpdatesOrCreatesRegistrationModelMixin,
                      IdentityFieldsMixin, ReviewFieldsMixin, PersonalFieldsMixin,
                      CitizenFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    class Meta(ConsentModelMixin.Meta):
        unique_together = ['subject_identifier', 'version']


class TestModel(NonUniqueSubjectIdentifierModelMixin, RequiresConsentModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta:
        consent_model = 'edc_consent.subjectconsent'
        consent_group = None
