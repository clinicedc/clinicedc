__all__ = ['SubjectConsent']

from edc_base.model_mixins import BaseUuidModel
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

from ..field_mixins import ReviewFieldsMixin, PersonalFieldsMixin, CitizenFieldsMixin, VulnerabilityFieldsMixin
from ..field_mixins.bw import IdentityFieldsMixin
from ..model_mixins import ConsentModelMixin


class SubjectConsent(ConsentModelMixin, NonUniqueSubjectIdentifierModelMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     IdentityFieldsMixin, ReviewFieldsMixin, PersonalFieldsMixin,
                     CitizenFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    class Meta(ConsentModelMixin.Meta):
        unique_together = ['subject_identifier', 'version']
