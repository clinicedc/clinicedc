from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from ..field_mixins import ReviewFieldsMixin, PersonalFieldsMixin, CitizenFieldsMixin
from ..field_mixins import VulnerabilityFieldsMixin, IdentityFieldsMixin
from ..model_mixins import ConsentModelMixin, RequiresConsentFieldsModelMixin


class SubjectConsent(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    IdentityFieldsMixin,
    ReviewFieldsMixin,
    PersonalFieldsMixin,
    CitizenFieldsMixin,
    VulnerabilityFieldsMixin,
    BaseUuidModel,
):
    class Meta(ConsentModelMixin.Meta):
        pass


class SubjectConsent2(
    ConsentModelMixin,
    SiteModelMixin,
    NonUniqueSubjectIdentifierModelMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    IdentityFieldsMixin,
    ReviewFieldsMixin,
    PersonalFieldsMixin,
    CitizenFieldsMixin,
    VulnerabilityFieldsMixin,
    BaseUuidModel,
):
    class Meta(ConsentModelMixin.Meta):
        pass


class TestModel(
    NonUniqueSubjectIdentifierModelMixin, RequiresConsentFieldsModelMixin, BaseUuidModel
):

    report_datetime = models.DateTimeField(default=get_utcnow)


class CrfOne(NonUniqueSubjectIdentifierModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)
