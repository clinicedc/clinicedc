from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow


class SubjectConsent(models.Model):

    subject_identifier = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField(default=get_utcnow)


# class Appointment(BaseUuidModel):
#
#     subject_identifier = models.CharField(max_length=25)
#
#     appt_datetime = models.DateTimeField(default=get_utcnow)
#
#     appt_reason = models.CharField(max_length=25)
#
#     visit_code = models.CharField(max_length=25)


class SubjectVisit(BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModel(models.Model):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)


class BadSubjectVisit(models.Model):

    appointment = models.ForeignKey(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
