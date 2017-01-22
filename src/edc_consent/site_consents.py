import copy
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import (
    SiteConsentError, AlreadyRegistered, ConsentError, ConsentPeriodError,
    ConsentVersionSequenceError, ConsentPeriodOverlapError, ConsentDoesNotExist)


class SiteConsents:

    def __init__(self):
        self.registry = []
        self._backup_registry = []

    def register(self, *consents):
        for consent in consents:
            if consent.name in [item.name for item in self.registry]:
                raise AlreadyRegistered(
                    'Consent already registered. Got {}'.format(str(consent)))
            self.check_consent_period_within_study_period(consent)
            self.check_consent_period_for_overlap(consent)
            self.check_version(consent)
            self.check_updates_versions(consent)
            self.registry.append(consent)

    def reset_registry(self):
        self.registry = []

    def backup_registry(self):
        """Backs up registry for tests."""
        self._backup_registry = copy.copy(self.registry)
        self.registry = []

    def restore_registry(self):
        """Restores registry for tests."""
        self.registry = copy.copy(self._backup_registry)
        self._backup_registry = []

    @property
    def consents(self):
        return sorted(self.registry, key=lambda x: x.name, reverse=False)

    def all(self):
        return self.consents

    def all_model_labels(self):
        return [consent.model_name for consent in self.registry]

    def all_subject_types(self):
        """Returns a list of consents by subject_type."""
        all_subject_types = {}
        for consent in self.registry:
            try:
                all_subject_types[consent.subject_type].append(consent)
            except KeyError:
                all_subject_types[consent.subject_type] = [consent]
        return sorted(all_subject_types, key=lambda x: x.subject_type, reverse=False)

    def get_consents_by_model(self, consent_model=None):
        """Returns a list of consents configured with the given consent model."""
        try:
            consent_model = consent_model._meta.label_lower
        except AttributeError:
            pass
        return [consent for consent in self.registry if consent.model_name == consent_model]

    def get_consents_by_version(self, consent_model=None, version=None):
        """Returns a list of consents of "version" configured with the given consent model."""
        consents = self.get_consents_by_model(consent_model)
        return [consent for consent in consents if consent.version == version]

    def get_all_by_version(self, version=None):
        """Returns a list of all consents using the given version regardless of the consent model."""
        return [consent for consent in self.registry if consent.version == version]

    def get_by_subject_type(self, subject_type=None):
        """Returns a list of all consents using the given subject_type regardless of the consent model."""
        return [consent for consent in self.registry if consent.subject_type == subject_type]

    def get_consent(self, report_datetime=None, consent_model=None, version=None, consent_group=None, **kwargs):
        """Return consent object valid for the datetime."""
        consents = []
        consent_group = consent_group or 'default'
        registered_consents = (
            c for c in self.registry if c.group == consent_group)
        for consent in registered_consents:
            if report_datetime:
                if consent_model and version:
                    if (consent.for_datetime(report_datetime)
                            and consent_model == consent.model_name
                            and version == consent.version):
                        consents.append(consent)
                elif consent_model or version:
                    if consent.for_datetime(report_datetime):
                        if consent_model == consent.model_name:
                            consents.append(consent)
                        if version == consent.version:
                            consents.append(consent)
                elif not consent_model and not version:
                    if consent.for_datetime(report_datetime):
                        consents.append(consent)
            elif not report_datetime:
                if (consent_model or version):
                    if consent_model and not version and consent_model == consent.model_name:
                        consents.append(consent)
                    if not consent_model and version and version == consent.version:
                        consents.append(consent)
        if not consents:
            raise ConsentDoesNotExist(
                'No matching consent in site consents. Using consent model=\'{}\', date={}, version={}. '.format(
                    consent_model, report_datetime, version))
        elif len(list(set([consent.name for consent in consents]))) > 1:
            raise ConsentError(
                'Multiple consents found, using consent model={}, date={}, version={}. Got {}'.format(
                    consent_model, report_datetime, version, consents))
        return consents[0]

    def check_updates_versions(self, new_consent):
        for version in new_consent.updates_versions:
            if not self.get_consents_by_version(consent_model=new_consent.model_name, version=version):
                raise ConsentVersionSequenceError(
                    'Consent version {1} cannot be an update to version(s) \'{0}\'. '
                    'Version \'{0}\' not found for \'{2}\''.format(
                        ', '.join(new_consent.updates_versions), version,
                        new_consent.model_name))

    def check_version(self, new_consent):
        if self.get_consents_by_version(
                consent_model=new_consent.model_name, version=new_consent.version):
            raise ConsentVersionSequenceError(
                'Consent version {update_versions} for \'{consent_model}.{version}\' is already registered'.format(
                    update_versions=', '.join(new_consent.updates_versions), version=new_consent.version,
                    consent_model=new_consent.model_name))

    def check_consent_period_for_overlap(self, new_consent):
        """Raises an error if consent period overlaps with a registered consent."""
        for consent in self.consents:
            if consent.model_name == new_consent.model_name:
                if (new_consent.start <= consent.start <= new_consent.end or
                        new_consent.start <= consent.end <= new_consent.end):
                    raise ConsentPeriodOverlapError(
                        'Consent periods overlap. Version \'{0}\' overlaps with version \'{1}\'. '
                        'Got {2} to {3} overlaps with {4} to {5}.'.format(
                            ', '.join(new_consent.updates_versions),
                            new_consent.version,
                            consent.start.strftime('%Y-%m-%d'),
                            consent.end.strftime('%Y-%m-%d'),
                            new_consent.start.strftime('%Y-%m-%d'),
                            new_consent.end.strftime('%Y-%m-%d')))

    def check_consent_period_within_study_period(self, new_consent):
        edc_protocol_app_config = django_apps.get_app_config('edc_protocol')
        study_open_datetime = edc_protocol_app_config.study_open_datetime
        study_close_datetime = edc_protocol_app_config.study_close_datetime
        for index, dt in enumerate([new_consent.start, new_consent.end]):
            if not (study_open_datetime <= dt <= study_close_datetime):
                raise ConsentPeriodError(
                    'Invalid consent. Consent period for {} must be within '
                    'study open/close dates of {} - {}. Got {}={}'.format(
                        new_consent.name,
                        study_open_datetime, study_close_datetime, 'start' if index == 0 else 'end', dt))

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers consent classes in the consents.py file of any INSTALLED_APP."""
        module_name = module_name or 'consents'
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(' * checking for site {} ...\n'.format(module_name))
        for app in django_apps.app_configs:
            writer(' * searching {}           \r'.format(app))
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_consents.registry)
                    import_module('{}.{}'.format(app, module_name))
                    writer(
                        ' * registered consents \'{}\' from \'{}\'\n'.format(module_name, app))
                except ConsentError as e:
                    writer('   - loading {}.consents ... '.format(app))
                    writer(style.ERROR('ERROR! {}\n'.format(str(e))))
                except ImportError as e:
                    site_consents.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteConsentError(str(e))
            except ImportError:
                pass
            except Exception as e:
                raise SiteConsentError(
                    'An {} was raised when loading site_consents. Got {}.'.format(e.__class__.__name__, str(e)))

site_consents = SiteConsents()
