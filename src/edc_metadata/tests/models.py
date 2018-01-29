from datetime import date
from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_base.model_mixins import BaseUuidModel
from edc_constants.choices import YES_NO
from edc_constants.constants import MALE
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_lab.models.model_mixins import PanelModelMixin
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_reference.model_mixins import ReferenceModelMixin, RequisitionReferenceModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins import OnScheduleModelMixin, OffScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin, CrfModelMixin

from ..model_mixins.creates import CreatesMetadataModelMixin
from ..model_mixins.updates import UpdatesCrfMetadataModelMixin
from ..model_mixins.updates import UpdatesRequisitionMetadataModelMixin


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):

    pass


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    class Meta(OffstudyModelMixin.Meta):
        pass


class DeathReport(UniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier, )


class SubjectConsent(UniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     BaseUuidModel):

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default='1')

    identity = models.CharField(max_length=25, default='111111111')

    confirm_identity = models.CharField(max_length=25, default='111111111')

    dob = models.DateField(default=date(1995, 1, 1))

    gender = models.CharField(max_length=25, default=MALE)

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier, )


class SubjectVisit(VisitModelMixin, ReferenceModelMixin,
                   CreatesMetadataModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=50)

    reason = models.CharField(max_length=25)


class SubjectRequisition(CrfModelMixin, RequisitionReferenceModelMixin,
                         PanelModelMixin,
                         UpdatesRequisitionMetadataModelMixin,
                         BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    requisition_datetime = models.DateTimeField(null=True)

    is_drawn = models.CharField(max_length=25, choices=YES_NO, null=True)

    reason_not_drawn = models.CharField(max_length=25, null=True)


class CrfOne(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
             BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class CrfTwo(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
             BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfThree(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
               BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfFour(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
              BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfFive(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
              BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class Crfsix(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
             BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfSeven(CrfModelMixin, ReferenceModelMixin, UpdatesCrfMetadataModelMixin,
               BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfMissingManager(ReferenceModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)
