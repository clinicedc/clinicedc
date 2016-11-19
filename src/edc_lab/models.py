from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_identifier.model_mixins import IdentifierModelMixin

from .model_mixins import (
    DestinationModelMixin, PackingListItemModelMixin, PackingListModelMixin, SpecimenCollectionModelMixin,
    SpecimenCollectionItemModelMixin)
from .managers import SpecimenCollectionItemManager, SpecimenCollectionManager


class ReceiveIdentifier(IdentifierModelMixin):

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'


class Destination(DestinationModelMixin, BaseUuidModel):

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'


class PackingListItem(PackingListItemModelMixin, BaseUuidModel):

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'


class PackingList(PackingListModelMixin, BaseUuidModel):

    destination = models.ForeignKey(
        Destination,
        verbose_name='Ship Specimens To',
        null=True)

    packing_list_item = models.ForeignKey(PackingListItem)

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'


class SpecimenCollection(SpecimenCollectionModelMixin, BaseUuidModel):

    objects = SpecimenCollectionManager()

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'


class SpecimenCollectionItem(SpecimenCollectionItemModelMixin, BaseUuidModel):

    specimen_collection = models.ForeignKey(SpecimenCollection)

    objects = SpecimenCollectionItemManager()

    history = HistoricalRecords()

    class Meta:
        app_label = 'edc_lab'
