from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.model_mixins import CreateAppointmentsMixin
from edc_appointment.models import Appointment
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_reference.model_mixins import ReferenceModelMixin, RequisitionReferenceModelMixin
from edc_visit_schedule.model_mixins import EnrollmentModelMixin, DisenrollmentModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin, CrfModelMixin

from ..model_mixins.creates import CreatesMetadataModelMixin
from ..model_mixins.updates import UpdatesCrfMetadataModelMixin
from ..model_mixins.updates import UpdatesRequisitionMetadataModelMixin


class Enrollment(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'


class Disenrollment(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    class Meta(OffstudyModelMixin.Meta):
        pass


class SubjectVisit(VisitModelMixin, ReferenceModelMixin,
                   CreatesMetadataModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=50)

    reason = models.CharField(max_length=25)


class SubjectRequisition(CrfModelMixin, RequisitionReferenceModelMixin,
                         UpdatesRequisitionMetadataModelMixin,
                         BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    panel_name = models.CharField(max_length=25)

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
