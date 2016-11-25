import random

from django.apps import apps as django_apps

from .exceptions import RequisitionError

edc_device_app_config = django_apps.get_app_config('edc_device')


class RequisitionIdentifier:

    def __init__(self, model=None):
        self.model = model
        self.device_id = edc_device_app_config.device_id
        self.template = '{device_id}{random_string}'
        self.identifier = self.template.format(device_id=self.device_id, random_string=self.random_string)
        if model:
            if self.is_duplicate:
                raise RequisitionError('Unable prepare a unique requisition identifier, '
                                       'all are taken. Increase the length of the random string')

    def __str__(self):
        return self.identifier

    @property
    def random_string(self):
        return ''.join([random.choice('ABCDEFGHKMNPRTUVWXYZ2346789') for _ in range(5)])

    @property
    def is_duplicate(self):
        is_duplicate = False
        if self.model.objects.filter(requisition_identifier=self.identifier):
            n = 1
            while self.model.objects.filter(requisition_identifier=self.identifier):
                self.identifier = self.template.format(device_id=self.device_id, random_string=self.random_string)
                n += 1
                if n == len('ABCDEFGHKMNPRTUVWXYZ2346789') ** 5:
                    is_duplicate = True
        return is_duplicate
