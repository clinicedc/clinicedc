from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow


class TestModel(BaseUuidModel):

    pass


class Condition(BaseUuidModel):

    name = models.CharField(max_length=25, default="anemia")


class AnyModel(BaseUuidModel):

    name = models.CharField(max_length=25, default="anemia")

    history = HistoricalRecords()


class AE(SiteModelMixin, BaseUuidModel):

    ae_grade = models.CharField(max_length=10)

    subject_identifier = models.CharField(max_length=10)

    conditions = models.ManyToManyField(Condition)

    history = HistoricalRecords()


class AeFollowup(SiteModelMixin, BaseUuidModel):

    ae = models.ForeignKey(AE, on_delete=models.PROTECT)

    subject_identifier = models.CharField(max_length=10)

    history = HistoricalRecords()


class Death(SiteModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=10)

    report_datetime = models.DateTimeField(default=get_utcnow)

    cause = models.CharField(max_length=10)

    history = HistoricalRecords()
