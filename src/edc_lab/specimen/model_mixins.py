from django.db import models
from django.utils import timezone

from edc_base.model.validators import datetime_not_future

from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier

from .constants import CONDITION_OK


class SpecimenCollectionModelMixin (models.Model):

    collection_identifier = models.CharField(
        verbose_name='Collection Identifier',
        max_length=25,
        editable=False,
        unique=True)

    collection_datetime = models.DateTimeField(
        verbose_name="Date and time received",
        default=timezone.now,
        validators=[datetime_not_future, ],
        db_index=True)

    def __str__(self):
        return self.collection_identifier

    def natural_key(self):
        return (self.collection_identifier, )

    class Meta:
        abstract = True


class SpecimenCollectionItemModelMixin (models.Model):

    specimen_identifier = models.CharField(
        verbose_name='Specimen Identifier',
        max_length=25)

    collection_condition = models.CharField(
        verbose_name='Condition of specimen',
        max_length=50,
        default=CONDITION_OK)

    def natural_key(self):
        return (self.specimen_identifier, )

    class Meta:
        abstract = True
