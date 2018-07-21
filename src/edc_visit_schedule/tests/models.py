from datetime import date
from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_base.model_mixins import BaseUuidModel
from edc_visit_tracking.model_mixins import CrfModelMixin, VisitModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin

from ..model_mixins import SubjectScheduleCrfModelMixin
from ..model_mixins import OffScheduleModelMixin, OnScheduleModelMixin


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)


class SubjectConsent(NonUniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     BaseUuidModel):

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default='1')

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))


class SubjectOffstudy(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


class DeathReport(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


# visit_schedule

class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):

    pass


class OnScheduleThree(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleThree(OffScheduleModelMixin, BaseUuidModel):

    pass


# visit_schedule_two

class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleTwo(OffScheduleModelMixin, BaseUuidModel):

    pass


class OnScheduleFour(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleFour(OffScheduleModelMixin, BaseUuidModel):

    pass


class CrfOne(SubjectScheduleCrfModelMixin, CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)
