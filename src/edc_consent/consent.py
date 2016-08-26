from django.apps import apps as django_apps
from django.conf import settings

from edc_base.utils.convert import localize


class Consent:

    def __init__(self, model, **kwargs):
        self.app_label, self.model_name = model.split('.')  # use model._meta.label_lower format
        self.end = kwargs.get('end')
        self.start = kwargs.get('start')
        self.updates_version = kwargs.get('updates_version', [])
        self.version = kwargs.get('version')
        self.gender = kwargs.get('gender', [])
        self.age_min = kwargs.get('age_min', 0)
        self.age_max = kwargs.get('age_max', 0)
        self.age_is_adult = kwargs.get('age_is_adult', 0)
        self.localize_dates()
        if self.updates_version:
            self.updates_version = ''.join([s for s in self.updates_version if s != ' '])
            self.updates_version = self.updates_version.split(',')

    def __str__(self):
        return '{}.{} version {}'.format(self.app_label, self.model_name, self.version)

    @property
    def label_lower(self):
        return '{}.{}'.format(self.app_label, self.model_name)

    @property
    def model(self):
        return django_apps.get_model(self.app_label, self.model_name)

    def slugify(self):
        return '{}-{}-{}'.format(self.app_label, self.model_name, self.version)

    def localize_dates(self):
        if settings.USE_TZ:
            if self.start:
                self.start = localize(self.start)
            if self.end:
                self.end = localize(self.end)

    def valid_for_datetime(self, consent_datetime):
        valid_for_datetime = False
        if self.start <= consent_datetime <= self.end:
            valid_for_datetime = True
        return valid_for_datetime
