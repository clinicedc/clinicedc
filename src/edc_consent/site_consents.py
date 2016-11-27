from edc_consent.exceptions import SiteConsentError, AlreadyRegistered
from django.utils import timezone


class SiteConsents:

    def __init__(self):
        self.registry = []

    def register(self, consent):
        for item in self.registry:
            if (item.valid_for_datetime(consent.start) and
                    item.valid_for_datetime(consent.end)):
                raise AlreadyRegistered('Consent already registered. Got {}'.format(str(consent)))
        self.registry.append(consent)

    def reset_registry(self):
        self.registry = []

    def all(self):
        return sorted(self.registry, key=lambda x: x.version, reverse=False)

    def all_model_labels(self):
        return [consent_config.label_lower for consent_config in self.registry]

    def all_subject_types(self):
        """Returns a dictionary of consent configs by subject_type."""
        all_subject_types = {}
        for consent_config in self.registry:
            try:
                all_subject_types[consent_config.subject_type].append(consent_config)
            except KeyError:
                all_subject_types[consent_config.subject_type] = [consent_config]
        return all_subject_types

    def get_label_lower(self, model):
        try:
            label_lower = model._meta.label_lower
        except AttributeError:
            label_lower = model
        return label_lower

    def get_consent_config(self, model, version=None, report_datetime=None, exception_cls=None):
        exception_cls = exception_cls or SiteConsentError
        if model not in self.all_model_labels():
            raise SiteConsentError(
                'Unknown consent model. Got {}. Registered consent models are: \'{}\'.'.format(
                    model, '\', \''.join(self.all_model_labels())))
        if report_datetime:
            return self.get_by_datetime(model, report_datetime, exception_cls)
        elif version:
            consent = self.get_by_version(model, version)
        else:
            consents = self.get_by_model(model)
            if len(consents) != 1:
                raise exception_cls('Multiple consent configurations returned.')
            consent = consents[0]
        return consent

    def get_by_model(self, model=None, exception_cls=None):
        """Returns a list of consents configured with the given consent model."""
        consents = []
        label_lower = self.get_label_lower(model)
        for consent in self.registry:
            if consent.label_lower == label_lower:
                consents.append(consent)
        return consents

    def get_by_version(self, model, version):
        """Returns a list of consents of "version" configured with the given consent model."""
        consents = []
        label_lower = self.get_label_lower(model)
        for consent in self.registry:
            if consent.version == version and consent.label_lower == label_lower:
                consents.append(consent)
        return consents

    def get_all_by_version(self, version):
        """Returns a list of all consents using the given version regardless of the consent model."""
        consents = []
        for consent in self.registry:
            if consent.version == version:
                consents.append(consent)
        return consents

    def get_by_subject_type(self, subject_type):
        """Returns a list of all consents using the given subject_type regardless of the consent model."""
        consents = []
        for consent in self.registry:
            if consent.subject_type == subject_type:
                consents.append(consent)
        return consents

    def get_by_datetime(self, consent_model, report_datetime, exception_cls=None):
        """Return consent_config object valid for the datetime."""
        exception_cls = exception_cls or SiteConsentError
        consent_configs = []
        for consent_config in self.registry:
            if consent_config.label_lower == consent_model and consent_config.valid_for_datetime(report_datetime):
                consent_configs.append(consent_config)
        if not consent_configs:
            raise exception_cls(
                'Cannot find a version for consent model \'{}\' using date \'{}\'. '
                'Check edc_consent.AppConfig.'.format(
                    consent_model,
                    timezone.localtime(report_datetime).strftime('%Y-%m-%d')))
        if len(consent_configs) > 1:
            raise exception_cls(
                'Multiple consents found, using consent model {} date {}. '
                'Check edc_consent.AppConfig.'.format(
                    consent_model, timezone.localtime(report_datetime).strftime('%Y-%m-%d')))
        return consent_configs[0]

site_consents = SiteConsents()
