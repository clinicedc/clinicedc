from django.apps import apps as django_apps
from django.conf import settings
from edc_base.utils.convert import localize


class AlreadyRegistered(Exception):
    pass


class ConsentType:

    def __init__(self, **kwargs):
        self.app_label = kwargs.get('app_label')
        self.model_name = kwargs.get('model_name')
        self.model_class = django_apps.get_model(self.app_label, self.model_name)
        self.verbose_name = self.model_class._meta.verbose_name
        self.start_datetime = kwargs.get('start_datetime')
        self.end_datetime = kwargs.get('end_datetime')
        self.localize_dates()
        self.version = kwargs.get('version')
        self.updates_version = kwargs.get('updates_version', [])
        if self.updates_version:
            self.updates_version = ''.join([s for s in self.updates_version if s != ' '])
            self.updates_version = self.updates_version.split(',')

    def __str__(self):
        return 'Consent {}.{} version {}'.format(self.app_label, self.model_name, self.version)

    def slugify(self):
        return '{}-{}-{}'.format(self.app_label, self.model_name, self.version)

    def localize_dates(self):
        if settings.USE_TZ:
            if self.start_datetime:
                self.start_datetime = localize(self.start_datetime)
            if self.end_datetime:
                self.end_datetime = localize(self.end_datetime)

    def valid_for_consent_model(self, consent_model):
        return self.valid_for_model(self, model=consent_model)

    def valid_for_model(self, model=None, app_label=None, model_name=None):
        valid_for_consent_model = False
        if not model:
            model = django_apps.get_model(app_label, model_name)
        if model._meta.app_label == self.app_label and model._meta.model_name == self.model_name:
            valid_for_consent_model = True
        return valid_for_consent_model

    def valid_for_datetime(self, consent_datetime):
        valid_for_datetime = False
        if self.start_datetime <= consent_datetime <= self.end_datetime:
            valid_for_datetime = True
        return valid_for_datetime
