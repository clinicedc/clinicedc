import sys
from copy import deepcopy

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import import_module, module_has_submodule


class AlreadyRegistered(Exception):
    pass


class SiteFormRunnerError(Exception):
    pass


class SiteFormRunners:
    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(self, runner=None):
        if "makemigrations" not in sys.argv:
            self._register(runner=runner)

    def _register(self, runner=None):
        if runner.model_name in self.registry:
            raise AlreadyRegistered(f"Form runner already registered. Got {runner}.")
        self.registry.update({runner.model_name: runner})

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers query rule classes in the form_runners.py file of
        any INSTALLED_APP.
        """
        module_name = module_name or "form_runners"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = deepcopy(site_form_runners.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered '{module_name}' from '{app}'\n")
                except SiteFormRunnerError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_form_runners.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteFormRunnerError(str(e))
            except ImportError:
                pass


site_form_runners = SiteFormRunners()
