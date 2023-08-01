from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_crf.model_mixins import CrfModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_lab.models import Panel
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import (
    OffScheduleModelMixin,
    OnScheduleModelMixin,
    VisitCodeFieldsModelMixin,
)
from edc_visit_tracking.models import SubjectVisit


class SubjectConsent(models.Model):
    subject_identifier = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField(default=get_utcnow)


# class SubjectVisit(VisitModelMixin, BaseUuidModel):
#     appointment = models.OneToOneField(Appointment, on_delete=PROTECT)
#
#     subject_identifier = models.CharField(max_length=25)
#
#     report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectRequisition(
    SiteModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    VisitCodeFieldsModelMixin,
    BaseUuidModel,
):
    @classmethod
    def related_visit_model_attr(cls):
        return "subject_visit"

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=models.PROTECT, related_name="+")

    panel = models.ForeignKey(Panel, on_delete=PROTECT)

    class Meta(BaseUuidModel.Meta):
        pass


class TestModel(models.Model):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)


class BadSubjectVisit(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)


class OnScheduleOne(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleOne(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleTwo(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleTwo(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class CrfOne(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class CrfTwo(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfThree(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfFour(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)


class CrfFive(CrfModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    f1 = models.CharField(max_length=50, null=True)
