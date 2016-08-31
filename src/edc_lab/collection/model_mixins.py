from django.db import models
from django.utils import timezone

from edc_base.model.validators import datetime_not_future
from edc_base.model.fields import InitialsField

from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier


class CollectionIdentifier(AlphanumericIdentifier):

    name = 'collectionidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']


class CollectionModelMixin (models.Model):

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

    requisition_identifier = models.CharField(
        verbose_name='Requisition Identifier',
        max_length=25,
        null=True,
        blank=True,
        db_index=True)

    drawn_datetime = models.DateTimeField(
        verbose_name="Date and time drawn",
        validators=[datetime_not_future, ],
        db_index=True)

    visit = models.CharField(
        verbose_name="Visit Code",
        max_length=25)

    clinician_initials = InitialsField()

    receive_condition = models.CharField(
        verbose_name='Condition of primary tube',
        max_length=50,
        null=True)

    import_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return self.receive_identifier

    def save(self, *args, **kwargs):
        if not self.id and not self.receive_identifier:
            self.collection_identifier = CollectionIdentifier().identifier
        self.subject_type = self.registered_subject.subject_type
        super(CollectionModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.receive_identifier, )

    class Meta:
        abstract = True
