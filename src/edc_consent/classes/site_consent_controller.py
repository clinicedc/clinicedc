import copy
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class SiteConsentController(object):

    CONSENT_UPDATE_MODEL = 1

    def __init__(self):
        self._registry = {}

    def register(self, consent_cls, consent_update_cls):

        if consent_cls._meta.object_name.lower() in self._registry:
            raise AlreadyRegistered('The class %s is already registered' % consent_cls._meta.object_name)
        # confirm edc_consent is in Consent Catalogue
        #if not ConsentCatalogue.objects.filter(content_type_map__model=consent_cls._meta.object_name.lower()):
        #    raise AttributeError('Unable to register edc_consent model {0}. Consent models must be listed in the Consent Catalogue.'.format(consent_cls._meta.object_name))
        self._registry.update({consent_cls._meta.object_name.lower(): (consent_cls, consent_update_cls)})

    def get_consent_update_model(self, consent_cls):
        if self._registry.get(consent_cls._meta.object_name.lower(), None):
            return self._registry.get(consent_cls._meta.object_name.lower())[self.CONSENT_UPDATE_MODEL]

    def autodiscover(self):
        """Searches all apps for :file:`consents.py` and registers."""
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                before_import_registry = copy.copy(consents._registry)
                import_module('%s.consents' % app)
            except:
                consents._registry = before_import_registry
                if module_has_submodule(mod, 'consents'):
                    raise
# A global to contain all consents instances from modules
consents = SiteConsentController()
