from django.db import models
from django.db.models.deletion import PROTECT

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_dashboard.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..managers import AliquotManager
from ..model_mixins import (
    AliquotModelMixin, AliquotStatusModelMixin, AliquotIdentifierModelMixin)
from .manifest import Manifest

human_readable_pattern = '^[0-9]{3}\-[0-9A-Z]{3}\-[0-9A-Z]{4}\-[0-9]{4}\-[0-9]{4}$'

pattern = '^[0-9]{3}[0-9A-Z]{3}[0-9A-Z]{4}[0-9]{4}[0-9]{4}$'


class Manager(AliquotManager, SearchSlugManager):
    pass


class Aliquot(AliquotModelMixin, AliquotIdentifierModelMixin,
              AliquotStatusModelMixin,
              SearchSlugModelMixin, BaseUuidModel):

    manifest = models.ForeignKey(
        Manifest, null=True, on_delete=PROTECT)

    objects = Manager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.aliquot_identifier

    @property
    def human_aliquot_identifier(self):
        """Returns a human readable aliquot identifier.
        """
        x = self.aliquot_identifier
        return '{}-{}-{}-{}-{}'.format(x[0:3], x[3:6], x[6:10], x[10:14], x[14:18])

    def get_slugs(self):
        slugs = [self.aliquot_identifier,
                 self.human_aliquot_identifier,
                 self.subject_identifier,
                 self.parent_identifier,
                 self.requisition_identifier]
        if self.manifest:
            slugs.append(self.manifest.manifest_identifier)
        return slugs

    class Meta(AliquotModelMixin.Meta):
        app_label = 'edc_lab'
