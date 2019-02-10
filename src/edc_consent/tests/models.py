from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

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
