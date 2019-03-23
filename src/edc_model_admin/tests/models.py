import uuid

from datetime import date
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from edc_appointment.models import Appointment
from edc_consent.model_mixins import ConsentModelMixin
from edc_consent.field_mixins import PersonalFieldsMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import MALE
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_lab.models.model_mixins import PanelModelMixin
from edc_lab.models.model_mixins import RequisitionModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_metadata.model_mixins.updates import UpdatesRequisitionMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_reference.model_mixins import (
    ReferenceModelMixin,
    RequisitionReferenceModelMixin,
)
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils.date import get_utcnow
from edc_visit_schedule.model_mixins import OnScheduleModelMixin, OffScheduleModelMixin
from edc_visit_tracking.model_mixins import CrfModelMixin, VisitModelMixin


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


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):
    class Meta(OffstudyModelMixin.Meta):
        pass


class DeathReport(UniqueSubjectIdentifierFieldMixin, SiteModelMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectConsent(
    ConsentModelMixin,
    PersonalFieldsMixin,
    UniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    identity = models.CharField(max_length=25, default="111111111")

    confirm_identity = models.CharField(max_length=25, default="111111111")

    dob = models.DateField(default=date(1995, 1, 1))

    gender = models.CharField(max_length=25, default=MALE)

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectVisit(
    VisitModelMixin,
    ReferenceModelMixin,
    CreatesMetadataModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=50)

    reason = models.CharField(max_length=25)


class SubjectRequisition(
    CrfModelMixin,
    RequisitionReferenceModelMixin,
    PanelModelMixin,
    UpdatesRequisitionMetadataModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    requisition_datetime = models.DateTimeField(null=True)

    is_drawn = models.CharField(max_length=25, choices=YES_NO, null=True)

    reason_not_drawn = models.CharField(max_length=25, null=True)


class BaseCrfModel(SiteModelMixin, models.Model):

    subject_identifier = models.CharField(max_length=25)

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=CASCADE)

    f1 = models.CharField(max_length=50, default=uuid.uuid4)

    @property
    def visit(self):
        return getattr(self, self.visit_model_attr())

    @classmethod
    def visit_model_attr(cls):
        return "subject_visit"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.subject_visit.subject_identifier
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CrfOne(BaseCrfModel, BaseUuidModel):
    pass


class CrfTwo(BaseCrfModel, CrfModelMixin, BaseUuidModel):

    pass


class CrfThree(BaseCrfModel, CrfModelMixin, BaseUuidModel):

    pass


class CrfFour(BaseCrfModel, CrfModelMixin, BaseUuidModel):

    pass


class CrfFive(BaseCrfModel, CrfModelMixin, BaseUuidModel):

    pass


class CrfSix(BaseCrfModel, CrfModelMixin, BaseUuidModel):

    pass


class CrfSeven(BaseCrfModel, CrfModelMixin, BaseUuidModel):

    pass


class Requisition(BaseCrfModel, RequisitionModelMixin, CrfModelMixin, BaseUuidModel):

    pass


class RedirectModel(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)


class RedirectNextModel(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)
