from django.conf import settings
from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow

from edc_crf.crf_model_mixin import CrfModelMixin
from edc_crf.crf_status_model_mixin import CrfStatusModelMixin


class Crf(CrfModelMixin, CrfStatusModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(settings.SUBJECT_VISIT_MODEL, on_delete=models.PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(BaseUuidModel.Meta):
        pass


class Prn(BaseUuidModel):

    subject_identifier = models.CharField(max_length=50, null=True, blank=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(BaseUuidModel.Meta):
        pass
