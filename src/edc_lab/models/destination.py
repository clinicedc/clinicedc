from edc_base.model.models import BaseUuidModel, HistoricalRecords

from ..managers import DestinationManager
from ..model_mixins import DestinationModelMixin


class Destination(DestinationModelMixin, BaseUuidModel):

    objects = DestinationManager()

    history = HistoricalRecords()

    class Meta(DestinationModelMixin.Meta):
        app_label = 'edc_lab'
