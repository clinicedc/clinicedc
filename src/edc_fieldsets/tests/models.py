from django.db import models
from edc_constants.choices import YES_NO
from edc_crf.model_mixins import CrfModelMixin, CrfWithActionModelMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
)


class SubjectVisit(VisitModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)


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


class MyModel(CrfModelMixin, BaseUuidModel):
    f1 = models.CharField(verbose_name="Are you circumcised?", max_length=10, choices=YES_NO)

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
