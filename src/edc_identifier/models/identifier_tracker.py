from django.db import models
from django.apps import apps as django_apps
from edc_base.model.models import BaseUuidModel

if django_apps.is_installed('edc_sync'):
    from edc_sync.models import SyncModelMixin
    identifier_tracker_parents = (SyncModelMixin, BaseUuidModel)
else:
    identifier_tracker_parents = (BaseUuidModel, )


class IdentifierTrackerManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierTracker(*identifier_tracker_parents):

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

    def __unicode__(self):
        return self.identifier

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['root_number', 'counter']
        unique_together = ['root_number', 'counter']
