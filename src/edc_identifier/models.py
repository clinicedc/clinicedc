from django.apps import apps as django_apps
from django.db import models

from edc_base.model_mixins import BaseModel, BaseUuidModel
from edc_base.model_managers import HistoricalRecords
from edc_base.utils import get_utcnow


class IdentifierModelManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class SubjectIdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierModelMixin(models.Model):
    """A model mixin for models that store identifiers as allocated."""

    identifier = models.CharField(max_length=36, unique=True, editable=False)
    padding = models.IntegerField(default=4, editable=False)
    sequence_number = models.IntegerField()
    device_id = models.IntegerField(default=0)
    is_derived = models.BooleanField(default=False)
    sequence_app_label = models.CharField(
        max_length=50, editable=False, default='identifier')
    sequence_model_name = models.CharField(
        max_length=50, editable=False, default='sequence')

    def __str__(self):
        return self.identifier

    def natural_key(self):
        return (self.identifier, self.device_id, )

    def save(self, *args, **kwargs):
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.device_id = edc_device_app_config.device_id
        if not self.id:
            if self.is_derived:
                self.sequence_number = 0
            else:
                Sequence = django_apps.get_model('edc_identifier', 'sequence')
                sequence = Sequence.objects.using(
                    kwargs.get('using')).create(device_id=self.device_id)
                self.sequence_number = sequence.pk
        super(IdentifierModelMixin, self).save(*args, **kwargs)

    @property
    def formatted_sequence(self):
        """Returns a padded sequence segment for the identifier"""
        if self.is_derived:
            return ''
        return str(self.sequence_number).rjust(self.padding, '0')

    class Meta:
        abstract = True


class IdentifierHistoryMixin(models.Model):

    identifier = models.CharField(
        max_length=25,
        unique=True
    )

    identifier_type = models.CharField(
        max_length=25,
    )

    identifier_prefix = models.CharField(
        max_length=25,
        null=True,
    )

    created_datetime = models.DateTimeField(
        default=get_utcnow)

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        abstract = True


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
