import copy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Controller(object):
    """Registers from modules with a edc_consent module (edc_consent.py)."""

    def __init__(self):
        self._registry = []
        self._group_names = []
        self._autodiscovered = None
        self._models = None

    def register(self, consent_cls):
        """Registers edc_consent classes to the registry (a list).

        Ensures model classes refered to by the trackers in the LabTracker classes
        have the following methods:
            * get_subject_identifier
            * get_report_datetime
            * get_result_datetime
            * get_test_code
        """
        if consent_cls in self._registry:
            raise AlreadyRegistered('The class %s is already registered' % consent_cls)
        if 'models' in dir(consent_cls):
            raise ImproperlyConfigured('Expected class attribute \'models\' for consent_cls {0}'.format(consent_cls))
        self._registry.append(consent_cls)

    def unregister(self, consent_cls):
        for index, cls in enumerate(self._registry):
            if consent_cls == cls:
                del self._registry[index]

    def all(self):
        """Returns the registry as a list."""
        return self._registry

    def autodiscover(self):
        """Searches all apps for :file:`lab_tracker.py` and registers
        all :class:`LabTracker` subclasses found."""
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                before_import_registry = copy.copy(site_consents._registry)
                import_module('%s.edc_consent' % app)
            except:
                site_consents._registry = before_import_registry
                if module_has_submodule(mod, 'edc_consent'):
                    raise

site_consents = Controller()
