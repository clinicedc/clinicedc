import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class RegistryNotLoaded(Exception):
    pass


class NotRegistered(Exception):
    pass


class AlreadyRegistered(Exception):
    pass


class SiteRandomizerError(Exception):
    pass


class SiteRandomizers:
    """Main controller of :class:`SiteRandomizers` objects."""

    def __init__(self):
        self._registry = {}
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                "Registry not loaded. Is AppConfig for 'edc_randomization' "
                "declared in settings?."
            )
        return self._registry

    def register(self, randomizer_cls):
        self.loaded = True
        if randomizer_cls.name not in self.registry:
            self.registry.update({randomizer_cls.name: randomizer_cls})
        else:
            raise AlreadyRegistered(
                f"Randomizer class for `{randomizer_cls}` is already registered. "
                f"Got name=`{randomizer_cls.name}`. See also `settings` attribute "
                "`EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER`."
            )

    def get(self, name):
        try:
            return self._registry[name]
        except KeyError:
            raise NotRegistered(
                f"A Randomizer class by this name is not registered. "
                f"Expected one of {list(self._registry.keys())}. "
                f"Got '{name}'. See site_randomizer."
            )

    def randomize(
        self,
        name,
        subject_identifier=None,
        report_datetime=None,
        site=None,
        user=None,
        **kwargs,
    ):
        randomizer_cls = self.get(name)
        return randomizer_cls(
            subject_identifier=subject_identifier,
            report_datetime=report_datetime,
            site=site,
            user=user,
            **kwargs,
        )

    def autodiscover(self, module_name=None, apps=None, verbose=None):
        """Autodiscovers classes in the randomizers.py file of
        any INSTALLED_APP.
        """
        self.loaded = True
        module_name = module_name or "randomizers"
        verbose = True if verbose is None else verbose
        if verbose:
            sys.stdout.write(f" * checking site for module '{module_name}' ...\n")
        for app in apps or django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_randomizers._registry)
                    import_module(f"{app}.{module_name}")
                    if verbose:
                        sys.stdout.write(" * registered randomizer from " f"'{app}'\n")
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        raise
                    site_randomizers._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ModuleNotFoundError:
                pass


site_randomizers = SiteRandomizers()
