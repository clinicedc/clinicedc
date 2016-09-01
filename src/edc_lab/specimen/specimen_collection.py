from django.apps import apps as django_apps

from .specimen import Specimen


app_config = django_apps.get_app_config('edc_lab')


class CollectionError(Exception):
    pass


class Collection:

    model = app_config.specimen_collection_model
    item_model = app_config.specimen_collection_item_model

    def __init__(self, collection_identifier=None):
        self.object = None
        self.specimens = {}
        self.collection_identifier = collection_identifier
        if collection_identifier:
            self.object = self.model.objects.get(
                collection_identifier=collection_identifier)

    def add(self, requisition):
        specimen = Specimen(requisition)
        try:
            specimen = self.item_model.objects.get(
                specimen_identifier=specimen.specimen_identifier)
            CollectionError('Specimen already collected. Got {} collected on {} manifest {}.'.format(
                specimen.specimen_identifier,
                specimen.specimen_collection.collection_datetime.date().isoformat(),
                specimen.specimen_collection.collection_identifier))
        except self.item_model.DoesNotExist:
            self.specimens.update({specimen.specimen_identifier: specimen})
