from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_base.model_mixins import BaseUuidModel
from edc_constants.choices import YES_NO
from edc_visit_tracking.model_mixins import VisitModelMixin
from edc_visit_tracking.model_mixins.crfs.crf_model_mixin import CrfModelMixin


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=25)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)


class MyModel(CrfModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    circumcised = models.CharField(
        verbose_name="Are you circumcised?",
        max_length=10,
        choices=YES_NO)
