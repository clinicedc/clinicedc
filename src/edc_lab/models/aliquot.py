from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_dashboard.model_mixins import SearchSlugModelMixin
from ..managers import AliquotManager
from ..model_mixins import (
    AliquotModelMixin, AliquotStatusModelMixin, AliquotIdentifierModelMixin)
from .manifest import Manifest


class Aliquot(AliquotModelMixin, AliquotIdentifierModelMixin,
              AliquotStatusModelMixin,
              SearchSlugModelMixin, BaseUuidModel):

    manifest = models.ForeignKey(Manifest, null=True)

    objects = AliquotManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.aliquot_identifier

    def get_slugs(self):
        slugs = [self.aliquot_identifier,
                 self.subject_identifier,
                 self.parent_identifier,
                 self.requisition_identifier]
        if self.manifest:
            slugs.append(self.manifest.manifest_identifier)
        return slugs

    class Meta(AliquotModelMixin.Meta):
        app_label = 'edc_lab'
