import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AlreadyRegistered, RegistryNotLoaded


class SiteLabs(object):

    def __init__(self):
        self._registry = {}
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'edc_lab\' '
                'declared in settings?.')
        return self._registry

    def get(self, lab_profile_name):
        return self._registry.get(lab_profile_name)

    def register(self, model, lab):
        self.loaded = True
        if model not in self.registry:
            self.registry.update({model: lab})
        else:
            raise AlreadyRegistered(
                'Lab profile {} is already registered.'.format(lab))

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the labs.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'labs'
        sys.stdout.write(' * checking for {} ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_labs._registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(
                        ' * registered labs from application \'{}\'\n'.format(app))
                except Exception as e:
                    if 'No module named \'{}.{}\''.format(app, module_name) not in str(e):
                        site_labs._registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
            except ImportError:
                pass

site_labs = SiteLabs()
