from django.db import models

from edc_base.model.models import BaseModel, BaseUuidModel, HistoricalRecords

from .model_mixins import IdentifierModelMixin, IdentifierHistoryMixin


class IdentifierModelManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class SubjectIdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class SubjectIdentifier(IdentifierModelMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['-created']


class Sequence(BaseModel):
    """A model that provides a unique sequence number using the integer auto field."""

    device_id = models.IntegerField(default=99)

    objects = models.Manager()

    def __str__(self):
        return self.pk

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['id', ]


class IdentifierModel(BaseUuidModel):

    name = models.CharField(max_length=50)

    sequence_number = models.IntegerField()

    identifier = models.CharField(max_length=50, unique=True)

    linked_identifier = models.CharField(max_length=50, null=True)

    device_id = models.IntegerField(default=99)

    protocol_number = models.CharField(max_length=3)

    model = models.CharField(max_length=50, null=True)

    subject_type = models.CharField(max_length=25, null=True)

    study_site = models.CharField(max_length=25)

    objects = IdentifierModelManager()

    def __str__(self):
        return '{} {}'.format(self.identifier, self.name)

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['sequence_number', ]
        unique_together = ('name', 'identifier')


class IdentifierTrackerManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierTracker(BaseUuidModel):

    """
    Used with class Identifier for non-subject identifiers
    """

    identifier = models.CharField(
        max_length=25,
        db_index=True)

    identifier_string = models.CharField(
        max_length=50,
        db_index=True)

    root_number = models.IntegerField(db_index=True)

    counter = models.IntegerField(db_index=True)

    identifier_type = models.CharField(
        max_length=35)

    device_id = models.CharField(
        max_length=10,
        null=True,
        blank=True)

    objects = IdentifierTrackerManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.identifier

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['root_number', 'counter']
        unique_together = ['root_number', 'counter']


class IdentifierHistoryManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierHistory(IdentifierHistoryMixin, BaseUuidModel):

    objects = IdentifierHistoryManager()

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_identifier'
