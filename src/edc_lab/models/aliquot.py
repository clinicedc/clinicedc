from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..managers import AliquotManager
from ..model_mixins.aliquot import (
    AliquotModelMixin, AliquotIdentifierModelMixin, AliquotTypeModelMixin,
    AliquotShippingMixin)


class Manager(AliquotManager, SearchSlugManager):
    pass


class Aliquot(AliquotModelMixin,
              AliquotIdentifierModelMixin,
              AliquotTypeModelMixin,
              AliquotShippingMixin,
              SearchSlugModelMixin, BaseUuidModel):

    search_slug_fields = [
        'aliquot_identifier',
        'human_readable_identifier',
        'subject_identifier',
        'parent_identifier',
        'requisition_identifier']

    objects = Manager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.aliquot_identifier

    @property
    def human_readable_identifier(self):
        """Returns a human readable aliquot identifier.
        """
        x = self.aliquot_identifier
        return '{}-{}-{}-{}-{}'.format(
            x[0:3], x[3:6], x[6:10], x[10:14], x[14:18])

    class Meta(AliquotModelMixin.Meta):
        app_label = 'edc_lab'
