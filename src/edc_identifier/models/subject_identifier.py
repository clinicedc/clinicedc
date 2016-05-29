from django.db import models
from django.apps import apps as django_apps

from edc_base.model.models import BaseUuidModel

from .base_identifier_model import BaseIdentifierModel

if django_apps.is_installed('edc_sync'):
    from edc_sync.models import SyncModelMixin
    subject_identifier_parents = (BaseIdentifierModel, SyncModelMixin, BaseUuidModel)
else:
    subject_identifier_parents = (BaseIdentifierModel, BaseUuidModel, )


class SubjectIdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class SubjectIdentifier(*subject_identifier_parents):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        app_label = 'edc_identifier'
        ordering = ['-created']
