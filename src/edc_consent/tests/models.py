from django.db import models
from django.db.models import PROTECT
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from ..field_mixins import (
    CitizenFieldsMixin,
    IdentityFieldsMixin,
    PersonalFieldsMixin,
    ReviewFieldsMixin,
    VulnerabilityFieldsMixin,
)
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


class SubjectVisit(SiteModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    # appointment = models.OneToOneField(Appointment, on_delete=CASCADE)
    # history = HistoricalRecords()
    pass


class TestModel(
    NonUniqueSubjectIdentifierModelMixin, RequiresConsentFieldsModelMixin, BaseUuidModel
):

    report_datetime = models.DateTimeField(default=get_utcnow)


# class CrfOne(
#     VisitTrackingCrfModelMixin,
#     ReferenceModelMixin,
#     UpdatesCrfMetadataModelMixin,
#     SiteModelMixin,
#     BaseUuidModel,
# ):
class CrfOne(NonUniqueSubjectIdentifierModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)
