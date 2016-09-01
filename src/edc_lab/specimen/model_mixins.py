from django.db import models
from django.utils import timezone

from edc_base.model.validators import datetime_not_future

from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier

from .constants import CONDITION_OK


class SpecimenCollectionIdentifier(AlphanumericIdentifier):

    name = 'collectionidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']


class SpecimenCollectionModelMixin (models.Model):

    collection_identifier = models.CharField(
        verbose_name='Collection Identifier',
        max_length=25,
        editable=False,
        db_index=True,
        unique=True)

    collection_datetime = models.DateTimeField(
        verbose_name="Date and time received",
        default=timezone.now,
        validators=[datetime_not_future, ],
        db_index=True)

    def __str__(self):
        return self.collection_identifier

    def save(self, *args, **kwargs):
        if not self.id and not self.receive_identifier:
            self.collection_identifier = SpecimenCollectionIdentifier().identifier
        self.subject_type = self.registered_subject.subject_type
        super(SpecimenCollectionModelMixin, self).save(*args, **kwargs)

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
