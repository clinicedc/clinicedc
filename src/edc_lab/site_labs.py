import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class AlreadyRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteLabsRequisitionModelError(Exception):
    pass


class SiteLabs:

    def __init__(self):
        self._registry = {}
        self.loaded = False

    def __repr__(self):
        return f'{self.__class__.__name__}(loaded={self.loaded})'

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'edc_lab\' '
                'declared in settings?.')
        return self._registry

    def get(self, lab_profile_name):
        if not self.loaded:
            raise RegistryNotLoaded(self)
        return self._registry.get(lab_profile_name)

    def register(self, lab_profile=None, requisition_model=None):
        """Registers a lab profile instance using the label_lower (model)
        as the key.

            requisition_model: label_lower string
            lab_profile: instance of LabProfile
        """
        if lab_profile:
            try:
                lab_profile.requisition_model = '.'.join(
                    requisition_model.split('.'))
            except AttributeError as e:
                raise SiteLabsRequisitionModelError(e) from e
            self.loaded = True
            value = self.registry.get(lab_profile.requisition_model)
            if value and value != lab_profile:
                raise AlreadyRegistered(
                    f'Lab profile {lab_profile} is already registered with '
                    f'model \'{lab_profile.requisition_model}\'.')
            elif lab_profile.name not in self.registry:
                self.registry.update({lab_profile.name: lab_profile})
                self.registry.update(
                    {lab_profile.requisition_model: lab_profile})
            else:
                raise AlreadyRegistered(
                    f'Lab profile {lab_profile} is already registered.')

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the labs.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'labs'
        sys.stdout.write(f' * checking for {module_name} ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_labs._registry)
                    import_module(f'{app}.{module_name}')
                    sys.stdout.write(
                        f' * registered labs from application \'{app}\'\n')
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        site_labs._registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
            except ImportError:
                pass


site_labs = SiteLabs()
