from django.db import models

from edc_base.model_mixins import BaseUuidModel


class IdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierHistory(BaseUuidModel):

    identifier = models.CharField(
        max_length=50,
        unique=True)

    identifier_type = models.CharField(
        max_length=50)

    objects = IdentifierManager()

    def natural_key(self):
        return self.identifier
