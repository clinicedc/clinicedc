from datetime import date

from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_consent.field_mixins import PersonalFieldsMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import MALE
from edc_crf.model_mixins import CrfWithActionModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import (
    UniqueSubjectIdentifierFieldMixin,
    UniqueSubjectIdentifierModelMixin,
)
from edc_lab.model_mixins import PanelModelMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel
from edc_reference.model_mixins import (
    ReferenceModelMixin,
    RequisitionReferenceModelMixin,
)
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
    VisitTrackingCrfModelMixin,
)

from ..model_mixins.creates import CreatesMetadataModelMixin
from ..model_mixins.updates import (
    UpdatesCrfMetadataModelMixin,
    UpdatesRequisitionMetadataModelMixin,
)


class CrfModelMixin(VisitTrackingCrfModelMixin, SiteModelMixin, models.Model):
    class Meta:
        abstract = True


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class DeathReport(UniqueSubjectIdentifierFieldMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)  # noqa


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()


class SubjectConsent(
    UniqueSubjectIdentifierModelMixin,
    PersonalFieldsMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    screening_identifier = models.CharField(max_length=25, null=True)

    identity = models.CharField(max_length=25, default="111111111")

    confirm_identity = models.CharField(max_length=25, default="111111111")

    dob = models.DateField(default=date(1995, 1, 1))

    gender = models.CharField(max_length=25, default=MALE)

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)  # noqa

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Consent"
        verbose_name_plural = "Subject Consents"


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
    BaseUuidModel,
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    requisition_datetime = models.DateTimeField(null=True)

    is_drawn = models.CharField(max_length=25, choices=YES_NO, null=True)

    reason_not_drawn = models.CharField(max_length=25, null=True)


class CrfOne(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class CrfTwo(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfThree(
    CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfFour(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfFive(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class Crfsix(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfSeven(
    CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class PrnOne(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class PrnTwo(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class MissedVisit(
    CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel
):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfMissingManager(ReferenceModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class SubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Missed Visit Reasons"
        verbose_name_plural = "Subject Missed Visit Reasons"


class SubjectVisitMissed(
    SubjectVisitMissedModelMixin,
    CrfWithActionModelMixin,
    BaseUuidModel,
):
    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="+"
    )

    class Meta(
        SubjectVisitMissedModelMixin.Meta,
        BaseUuidModel.Meta,
    ):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"
