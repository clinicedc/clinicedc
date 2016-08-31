from django.db import models

from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc_identifier.models import BaseIdentifierModel
from edc_lab.packing.model_mixins import DestinationModelMixin, PackingListItemModelMixin

from .packing.model_mixins import PackingListModelMixin


class ReceiveIdentifier(BaseIdentifierModel):

    class Meta:
        app_label = 'edc_lab'


class Destination(DestinationModelMixin, BaseUuidModel):
    class Meta:
        app_label = 'edc_lab'


class PackingListItem(PackingListItemModelMixin, BaseUuidModel):

    class Meta:
        app_label = 'edc_lab'


class PackingList(PackingListModelMixin, BaseUuidModel):

    destination = models.ForeignKey(
        Destination,
        verbose_name='Ship Specimens To',
        null=True)

    packing_list_item = models.ForeignKey(PackingListItem)

    class Meta:
        app_label = 'edc_lab'


