from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_constants.choices import YES_NO
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from edc_visit_tracking.model_mixins import VisitModelMixin, VisitTrackingCrfModelMixin


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)


class MyModel(VisitTrackingCrfModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(
        verbose_name="Are you circumcised?", max_length=10, choices=YES_NO
    )

    f2 = models.CharField(max_length=10, null=True, blank=True)

    f3 = models.CharField(max_length=10, null=True, blank=False)

    f4 = models.CharField(max_length=10, null=True, blank=False)

    f5 = models.CharField(max_length=10, null=True, blank=False)

    summary_one = models.CharField(max_length=10, null=True, blank=True)

    summary_two = models.CharField(max_length=10, null=True, blank=True)


class MyModel2(MyModel):
    class Meta:
        proxy = True


class MyModel3(MyModel):
    class Meta:
        proxy = True
