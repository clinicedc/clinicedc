from django.apps import apps as django_apps

from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier


app_config = django_apps.get_app_config('edc_lab')


class SpecimenCollectionError(Exception):
    pass


class SpecimenCollectionIdentifier(AlphanumericIdentifier):

    name = 'collectionidentifier'
    alpha_pattern = r'^[A-Z]{3}$'
    numeric_pattern = r'^[0-9]{4}$'
    seed = ['AAA', '0000']


class SpecimenCollection:

    model = app_config.specimen_collection_model
    item_model = app_config.specimen_collection_item_model

    def __init__(self, collection_identifier=None):
        self.object = None
        self.specimens = {}
        self.collection_identifier = collection_identifier
        try:
            self.object = self.model.objects.get(
                collection_identifier=collection_identifier)
        except self.model.DoesNotExist as e:
            if self.collection_identifier:
                raise self.model.DoesNotExist(e)
            else:
                self.collection_identifier = SpecimenCollectionIdentifier(
                ).identifier
                self.object = self.model.objects.create(
                    collection_identifier=self.collection_identifier)

    def add(self, specimen):
        try:
            specimen_collection_item = self.item_model.objects.get(
                specimen_identifier=specimen.specimen_identifier)
            SpecimenCollectionError(
                'Specimen already collected. Got {} collected on {} manifest {}.'.format(
                    specimen_collection_item.specimen_identifier,
                    specimen_collection_item.specimen_collection.collection_datetime.date(
                    ).isoformat(),
                    specimen_collection_item.specimen_collection.collection_identifier))
        except self.item_model.DoesNotExist:
            specimen_collection_item = self.item_model.objects.create(
                specimen_identifier=specimen.specimen_identifier,
                specimen_collection=self.object)
            self.specimens.update({specimen.specimen_identifier: specimen})
