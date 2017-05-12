import random

from django.apps import apps as django_apps

edc_device_app_config = django_apps.get_app_config('edc_device')


class DuplicateIdentifierError(Exception):
    pass


class SimpleIdentifier:

    """Usage:

        class ManifestIdentifier(Identifier):
            random_string_length = 9
            identifier_attr = 'manifest_identifier'
            template = 'M{device_id}{random_string}'
    """

    random_string_length = 5
    identifier_attr = 'identifier'
    model = None
    error_class = DuplicateIdentifierError
    template = '{device_id}{random_string}'

    def __init__(self, model=None, identifier_type=None):
        self.model = model or self.model
        self.identifier_type = identifier_type or self.identifier_type
        self.device_id = edc_device_app_config.device_id
        self.identifier = self.template.format(
            device_id=self.device_id, random_string=self.random_string)
        if self.is_duplicate:
            raise self.error_class(
                'Unable prepare a unique identifier, '
                'all are taken. Increase the length of the random string')
        self.model_class.objects.create(
            identifier=self.identifier, identifier_type=self.identifier_type)

    def __str__(self):
        return self.identifier

    @property
    def random_string(self):
        return ''.join(
            [random.choice('ABCDEFGHKMNPRTUVWXYZ2346789') for _ in range(
                self.random_string_length)])

    @property
    def model_class(self):
        return django_apps.get_model(*self.model.split('.'))

    @property
    def is_duplicate(self):
        is_duplicate = False
        if self.model_class.objects.filter(
                identifier=self.identifier, identifier_type=self.identifier_type):
            n = 1
            while self.model_class.objects.filter(
                    identifier=self.identifier, identifier_type=self.identifier_type):
                self.identifier = self.template.format(
                    device_id=self.device_id, random_string=self.random_string)
                n += 1
                if n == len('ABCDEFGHKMNPRTUVWXYZ2346789') ** self.random_string_length:
                    is_duplicate = True
        return is_duplicate
