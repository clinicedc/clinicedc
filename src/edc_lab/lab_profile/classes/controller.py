import copy

from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from ..exceptions import AlreadyRegistered


class ProfileController(object):

    """A controller for lab profiles handled within the EDC client."""

    def __init__(self):
        self.registry = {}
        self.group_model_registry = {}
        self.group_models = {}  # group models for each profile are the same!

    def add_registry_item(self, lab_profile):
        if lab_profile.name in self.registry:
            raise AlreadyRegistered('Lab profile {0} is already registered'.format(lab_profile.name))
        self.registry.update({lab_profile.name: lab_profile})
        self.update_group_models(lab_profile)

    def update_group_models(self, lab_profile):
        """Updates the group model registry allowing for convenient access to shared models.

        Grouped lab profiles share these models on the profile_group_name."""
        if not self.group_models:
            self.group_models.update({'receive': lab_profile.receive_model})
            self.group_models.update({'aliquot': lab_profile.aliquot_model})
            self.group_models.update({'panel': lab_profile.panel_model})
            self.group_models.update({'aliquot_type': lab_profile.aliquot_type_model})
            self.group_models.update({'profile': lab_profile.profile_model})
            self.group_models.update({'profile_item': lab_profile.profile_item_model})
        self.group_model_registry.update({lab_profile.profile_group_name: self.group_models})

    def get(self, name):
        return self.registry.get(name)

    def get_group_models(self, profile_group_name):
        return self.group_model_registry.get(profile_group_name)

    def register(self, lab_profile):
        self.add_registry_item(lab_profile)

    def autodiscover(self):
        """ Autodiscover rules from a specimen_manager module."""
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                before_import_registry = copy.copy(site_lab_profiles.registry)
                import_module('%s.lab_profiles' % app)
            except:
                site_lab_profiles.registry = before_import_registry
                if module_has_submodule(mod, 'lab_profiles'):
                    raise

site_lab_profiles = ProfileController()
