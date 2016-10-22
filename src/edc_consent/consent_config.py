from django.apps import apps as django_apps
from django.conf import settings

from edc_base.utils.convert import localize
from edc_consent.exceptions import SiteConsentError, AlreadyRegistered
from edc_consent.site_consents import site_consents


class ConsentConfig:

    def __init__(self, model, **kwargs):
        self.app_label, self.model_name = model.split('.')  # use model._meta.label_lower format
        self.end = kwargs.get('end')
        self.start = kwargs.get('start')
        self.updates_version = kwargs.get('updates_version', [])
        self.version = kwargs.get('version', '0')
        self.gender = kwargs.get('gender', [])
        self.age_min = kwargs.get('age_min', 0)
        self.age_max = kwargs.get('age_max', 0)
        self.age_is_adult = kwargs.get('age_is_adult', 0)
        self.subject_type = kwargs.get('subject_type', 'subject')
        self.localize_dates()
        self.check_version()
        self.check_consent_period()
        if self.updates_version:
            self.updates_version = ''.join([s for s in self.updates_version if s != ' '])
            self.updates_version = self.updates_version.split(',')
            self.check_updates_version()

    def __str__(self):
        return '{}.{} version {}'.format(self.app_label, self.model_name, self.version)

    @property
    def label_lower(self):
        return '{}.{}'.format(self.app_label, self.model_name)

    def slugify(self):
        return '{}-{}-{}'.format(self.app_label, self.model_name, self.version)

    @property
    def model(self):
        return django_apps.get_model(self.app_label, self.model_name)

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

    def check_updates_version(self):
        for version in self.updates_version:
            if not site_consents.get_by_version(self.label_lower, version):
                raise SiteConsentError(
                    'Consent version {1} cannot be an update to version(s) \'{0}\'. '
                    'Version \'{0}\' not found in \'{2}\''.format(
                        ', '.join(self.updates_version), self.version,
                        self.label_lower))

    def check_version(self):
        if site_consents.get_by_version(self.label_lower, self.version):
            raise AlreadyRegistered(
                'Consent version {1} for \'{2}.{3}\' is already registered'.format(
                    ', '.join(self.updates_version), self.version,
                    self.label_lower))

    def check_consent_period(self):
        registry = [consent_config
                    for consent_config in site_consents.all()
                    if consent_config.slugify() != self.slugify()]
        for consent_config in registry:
            if consent_config.label_lower == self.label_lower:
                if (self.start <= consent_config.start <= self.end or
                        self.start <= consent_config.end <= self.end):
                    raise AlreadyRegistered(
                        'Consent period for version \'{0}\' overlaps with version \'{1}\'. '
                        'Got {2} to {3} overlaps with {4} to {5}.'.format(
                            ', '.join(self.updates_version),
                            self.version,
                            consent_config.start.strftime('%Y-%m-%d'),
                            consent_config.end.strftime('%Y-%m-%d'),
                            self.start.strftime('%Y-%m-%d'),
                            self.end.strftime('%Y-%m-%d')))
