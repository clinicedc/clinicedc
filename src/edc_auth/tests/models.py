from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_randomization.models import RandomizationListModelMixin


class PiiModel(models.Model):

    name = models.CharField(max_length=50, null=True)

    class Meta:
        permissions = (("be_happy", "Can be happy"),)


class AuditorModel(models.Model):

    name = models.CharField(max_length=50, null=True)

    class Meta:
        permissions = (("be_sad", "Can be sad"),)


class TestModel(BaseUuidModel):

    name = models.CharField(max_length=50, null=True)


class SubjectRequisition(BaseUuidModel):

    name = models.CharField(max_length=50, null=True)

    history = HistoricalRecords()


class SubjectConsent(models.Model):

    name = models.CharField(max_length=50, null=True)

    history = HistoricalRecords()


class SubjectReconsent(models.Model):

    name = models.CharField(max_length=50, null=True)

    history = HistoricalRecords()


class CustomRandomizationList(RandomizationListModelMixin, BaseUuidModel):

    pass
