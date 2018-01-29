import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule
from django.core.exceptions import ObjectDoesNotExist


class AlreadyRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteLabsRequisitionModelError(Exception):
    pass


class SiteLabs:

    panel_model = 'edc_lab.panel'

    def __init__(self):
        self._registry = {}
        self.loaded = False
        self.migrated = False
        self.aliquot_types = {}

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

    def register(self, lab_profile=None):
        """Registers a lab profile instance using the label_lower (model)
        as the key.

            requisition_model: label_lower string
            lab_profile: instance of LabProfile
        """
        if lab_profile:
            self.loaded = True
            if lab_profile.name not in self.registry:
                self.registry.update({lab_profile.name: lab_profile})
                self.registry.update(
                    {lab_profile.requisition_model: lab_profile})
                self.aliquot_types.update(**lab_profile.aliquot_types)
                if self.migrated:
                    panel_model_cls = django_apps.get_model(self.panel_model)
                    self.update_panel_model(panel_model_cls=panel_model_cls)
            else:
                raise AlreadyRegistered(
                    f'Lab profile {lab_profile} is already registered.')

    def update_panel_model(self, panel_model_cls=None, **kwargs):
        """Updates or creates panel mode instances.

        Initially called in the post_migrate signal.
        """
        for lab_profile in self.registry.values():
            for panel in lab_profile.panels.values():
                try:
                    panel_model_obj = panel_model_cls.objects.get(
                        name=panel.name,
                        lab_profile_name=lab_profile.name)
                except ObjectDoesNotExist:
                    panel_model_cls.objects.create(
                        name=panel.name,
                        display_name=panel.verbose_name,
                        lab_profile_name=lab_profile.name)
                else:
                    panel_model_obj.display_name = panel.verbose_name
                    panel_model_obj.save()

    def autodiscover(self, module_name=None, verbose=False):
        """Autodiscovers classes in the labs.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'labs'
        verbose = True if verbose is None else verbose
        sys.stdout.write(f' * checking for {module_name} ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_labs._registry)
                    import_module(f'{app}.{module_name}')
                    if verbose:
                        sys.stdout.write(
                            f' * registered labs from application \'{app}\'\n')
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        site_labs._registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
            except ModuleNotFoundError:
                pass


site_labs = SiteLabs()
