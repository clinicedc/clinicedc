import sys

from copy import deepcopy
from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule


class AlreadyRegistered(Exception):
    pass


class SiteDataManagerError(Exception):
    pass


class SiteDataManager:
    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, rule_handler=None):
        if rule_handler.name in self.registry:
            raise AlreadyRegistered(
                f"Query rule_handler already registered. Got {rule_handler}."
            )
        self.registry.update({rule_handler.name: rule_handler})

    def get_rule_handler(self, name):
        name = name or "default"
        if name not in self.registry:
            raise SiteDataManagerError(
                f"Query rule handler is not registered. Got {name}."
            )
        return self.registry.get(name)

    def get_rule_handlers(self, model_name=None):
        rule_handlers = []
        if model_name:
            for k, v in self.registry.items():
                try:
                    if v.model_name == model_name:
                        rule_handlers.update({k: v})
                except AttributeError:
                    rule_handlers.append(v)
        else:
            return list(self.registry.values())
        return rule_handlers

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers query rule classes in the data_manager.py file of
        any INSTALLED_APP.
        """
        module_name = module_name or "data_manager"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for data manager {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = deepcopy(site_data_manager.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered '{module_name}' from '{app}'\n")
                except SiteDataManagerError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_data_manager.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteDataManagerError(str(e))
            except ImportError:
                pass


site_data_manager = SiteDataManager()
