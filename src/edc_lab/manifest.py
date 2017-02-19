from django.apps import apps as django_apps


class ManifestError(Exception):
    pass


class Manifest:

    destination_model_name = 'edc_lab.destination'

    def __init__(self, destinations=None, default_destination=None, destination_model_name=None):
        self.destination_model_name = destination_model_name or self.destination_model_name
        self.destinations = destinations
        self.default_destination = default_destination
        if default_destination not in destinations:
            raise ManifestError(
                'Invalid destination. Expected one of {}'.format(destinations))

    @property
    def destination_model(self):
        return django_apps.get_model(*self.destination_model_name.split('.'))

    def update_destinations(self):
        for name, description in self.destinations.items():
            try:
                self.destination_model.objects.get(name=name)
            except self.destination_model.DoesNotExist:
                self.destination_model.objects.create(
                    name=name,
                    description=description)
