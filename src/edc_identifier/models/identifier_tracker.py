from django.db import models

# from edc_base.model.models import BaseUuidModel
# from edc_sync.models import SyncModelMixin


class IdentifierTrackerManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierTracker(models.Model):

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
