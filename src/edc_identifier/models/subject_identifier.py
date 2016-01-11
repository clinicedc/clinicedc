from django.db import models

# from edc_base.model.models import BaseUuidModel
# from edc_sync.models import SyncModelMixin

from .base_identifier_model import BaseIdentifierModel


class SubjectIdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class SubjectIdentifier(BaseIdentifierModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['-created']
