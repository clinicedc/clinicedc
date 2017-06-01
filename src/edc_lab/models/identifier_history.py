from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_identifier.models import IdentifierHistoryMixin


class IdentifierManager(models.Manager):

    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)


class IdentifierHistory(IdentifierHistoryMixin, BaseUuidModel):

    objects = IdentifierManager()
