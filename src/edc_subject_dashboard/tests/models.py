from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.utils import get_utcnow
from edc_appointment.models import Appointment


class SubjectVisit(models.Model):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModel(models.Model):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)


class SubjectLocator(models.Model):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)


class BadSubjectVisit(models.Model):

    appointment = models.ForeignKey(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
