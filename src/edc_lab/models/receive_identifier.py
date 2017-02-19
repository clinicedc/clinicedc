from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_identifier.models import IdentifierModelMixin


class ReceiveIdentifier(IdentifierModelMixin, BaseUuidModel):

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'
