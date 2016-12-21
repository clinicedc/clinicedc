from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_identifier.models import IdentifierModelMixin

from .managers import AliquotManager, SpecimenCollectionItemManager, SpecimenCollectionManager
from .model_mixins import (
    AliquotModelMixin, DestinationModelMixin, PackingListItemModelMixin, PackingListModelMixin,
    SpecimenCollectionModelMixin, SpecimenCollectionItemModelMixin)


class Aliquot(AliquotModelMixin, BaseUuidModel):

    objects = AliquotManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.aliquot_identifier

    class Meta(AliquotModelMixin.Meta):
        app_label = 'edc_lab'


class SpecimenCollection(SpecimenCollectionModelMixin, BaseUuidModel):

    objects = SpecimenCollectionManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.collection_identifier

    class Meta(SpecimenCollectionModelMixin.Meta):
        app_label = 'edc_lab'


class SpecimenCollectionItem(SpecimenCollectionItemModelMixin, BaseUuidModel):

    specimen_collection = models.ForeignKey(SpecimenCollection)

    objects = SpecimenCollectionItemManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.specimen_identifier

    class Meta(SpecimenCollectionItemModelMixin.Meta):
        app_label = 'edc_lab'


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
