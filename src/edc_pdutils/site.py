import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class AlreadyRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteDataframeHandlerNotFound(Exception):
    pass


class Site:
    def __init__(self):
        self.registry = {}
        self.model_reference_registry = {}
        self.loaded = False

    def register(self, handler_cls=None, app_labels=None, models=None):
        app_labels = app_labels or []
        models = models or []
        name = handler_cls.__name__
        if name in self.registry:
            raise AlreadyRegistered(
                f"Dataframe handler class already been registered. " f"Got {name}"
            )
        self.registry.update({name: handler_cls})
        for app_label in app_labels:
            self.model_reference_registry.update({app_label: name})
        for model in models:
            self.model_reference_registry.update({model: name})
        self.loaded = True

    def get_for(self, key=None):
        if not self.loaded:
            raise RegistryNotLoaded("site_dataframe_handlers not loaded")
        handler_cls = None
        try:
            handler_cls = self.registry[key]
        except KeyError:
            pass
        try:
            handler_cls = self.registry[self.model_reference_registry.get(key)]
        except KeyError:
            pass
        try:
            handler_cls = self.registry[self.model_reference_registry.get(key.split(".")[0])]
        except KeyError:
            pass
        if not handler_cls:
            keys = list(self.registry.keys()) + list(self.model_reference_registry.keys())
            raise SiteDataframeHandlerNotFound(
                f"Cannot find dataframe hander. Got {key}. " f"Expected one of {keys}."
            )
        return handler_cls

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the site_dataframe_handlers.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or "site_dataframe_handlers"
        sys.stdout.write(f" * checking for {module_name} ...\n")
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_dataframe_handlers.registry)
                    import_module(f"{app}.{module_name}")
                    sys.stdout.write(
                        f" * registered dataframe handler from application '{app}'\n"
                    )
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        site_dataframe_handlers.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
            except ModuleNotFoundError:
                pass


site_dataframe_handlers = Site()
