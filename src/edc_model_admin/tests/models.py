import uuid

from django.db import models
from edc_consent.field_mixins import PersonalFieldsMixin
from edc_consent.field_mixins.identity_fields_mixin import IdentityFieldsMixin
from edc_consent.model_mixins import ConsentModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_lab.model_mixins import RequisitionModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.model_mixins import OnScheduleModelMixin, OffScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin, VisitModelMixin
from edc_visit_schedule.model_mixins.subject_on_schedule_model_mixin import (
    SubjectOnScheduleModelMixin,
)
from edc_visit_schedule.model_mixins.visit_schedule_model_mixins import (
    VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
)


class BasicModel(SiteModelMixin, BaseUuidModel):

    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)
    f3 = models.CharField(max_length=10, null=True, blank=False)
    f4 = models.CharField(max_length=10, null=True, blank=False)
    f5 = models.CharField(max_length=10)
    f5_other = models.CharField(max_length=10, null=True)
    subject_identifier = models.CharField(max_length=25, default="12345")


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):

    pass


class DeathReport(UniqueSubjectIdentifierFieldMixin, SiteModelMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectConsent(
    ConsentModelMixin,
    PersonalFieldsMixin,
    IdentityFieldsMixin,
    UniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    SiteModelMixin,
    SubjectOnScheduleModelMixin,
    VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
    BaseUuidModel,
):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectVisit(
    VisitModelMixin, CreatesMetadataModelMixin, SiteModelMixin, BaseUuidModel
):
    def update_reference_on_save(self):
        pass


class Requisition(RequisitionModelMixin, BaseUuidModel):
    def update_reference_on_save(self):
        pass


class BaseCrfModel(VisitTrackingCrfModelMixin, SiteModelMixin, models.Model):

    f1 = models.CharField(max_length=50, default=uuid.uuid4)

    class Meta:
        abstract = True


class CrfOne(BaseCrfModel, BaseUuidModel):
    pass


class CrfTwo(BaseCrfModel, BaseUuidModel):

    pass


class CrfThree(BaseCrfModel, BaseUuidModel):

    pass


class CrfFour(BaseCrfModel, BaseUuidModel):

    pass


class CrfFive(BaseCrfModel, BaseUuidModel):

    pass


class CrfSix(BaseCrfModel, BaseUuidModel):

    pass


class CrfSeven(BaseCrfModel, BaseUuidModel):

    pass


class RedirectModel(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)


class RedirectNextModel(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)
