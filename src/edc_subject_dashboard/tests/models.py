from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from edc_visit_tracking.model_mixins import VisitModelMixin


class SubjectConsent(models.Model):

    subject_identifier = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField(default=get_utcnow)


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModel(models.Model):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)


class BadSubjectVisit(models.Model):

    appointment = models.ForeignKey(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
