from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_sites.models import SiteModelMixin


class SubjectVisit(SiteModelMixin, SearchSlugModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)

    objects = SearchSlugManager()

    def get_search_slug_fields(self):
        fields = ["subject_identifier", "reason"]
        return fields


class TestModel(models.Model):
    f1 = models.CharField(max_length=25, null=True)

    class Meta:
        ordering = ("f1",)


class SubjectConsent(models.Model):
    name = models.CharField(max_length=50, null=True)

    history = HistoricalRecords()


class SubjectReconsent(models.Model):
    name = models.CharField(max_length=50, null=True)

    history = HistoricalRecords()


class SubjectRequisition(models.Model):
    name = models.CharField(max_length=50, null=True)

    history = HistoricalRecords()
