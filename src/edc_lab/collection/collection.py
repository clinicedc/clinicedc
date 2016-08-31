from django.apps import apps as django_apps
from edc_lab.collection.specimen import Specimen


app_config = django_apps.get_app_config('edc_lab')


class CollectionError(Exception):
    pass


class Collection:

    def __init__(self):
        self.specimens = {}

    def add(self, requisition):
        specimen = Specimen(requisition)
        try:
            colllection = app_config.aliquot_model.objects.get(
                specimen_identifier=specimen.specimen_identifier,
                is_collected=True)
            CollectionError('Specimen already collected. Got {} collected on {}.'.format(
                specimen.specimen_identifier,
                colllection.collection_datetime.date().isoformat()))
        except app_config.collection_model.DoesNotExist:
            self.specimens.update({specimen.specimen_identifier: specimen})
