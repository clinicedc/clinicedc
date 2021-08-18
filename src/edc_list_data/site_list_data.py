import copy
import sys
from importlib import import_module

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from django.db import transaction

from .load_list_data import LoadListDataError
from .preload_data import PreloadData


class AlreadyRegistered(Exception):
    pass


class AlreadyLoaded(Exception):
    pass


class SiteListDataError(Exception):
    pass


def get_autodiscover_enabled():
    return getattr(settings, "EDC_LIST_DATA_ENABLE_AUTODISCOVER", True)


class SiteListData:

    """Load list data from any module named "list_data".

    Called in AppConfig or by management command.
    """

    default_module_prefixes = ["edc_"]
    default_module_name = "list_data"

    def __init__(self, module_name=None):
        self.registry = {}
        self.app_names = []
        self.models = []
        self.module_name = module_name or self.default_module_name

    def initialize(self, module_name=None):
        self.__init__(module_name=module_name)

    def register(self, module, app_name=None):
        """Registers but does NOT `load` list_data."""
        if app_name and app_name in self.app_names:
            raise AlreadyLoaded(f"App already loaded. Got {app_name}.")
        else:
            self.app_names.append(app_name)
            opts = copy.deepcopy(self._get_options(module))
            sys.stdout.write(f"   + registered {self.module_name} from '{module.__name__}'\n")
            if opts.get(self.module_name):
                self._replace_list_data_or_raise_on_duplicate(module, opts)
            self.registry[module.__name__] = opts

    def load_data(self) -> None:
        """Calls `load` class with each list_data dictionary module to
        update database `list` tables.
        """
        style = color_style()
        for module_name, opts in self.registry.items():
            sys.stdout.write(f"   - loading {module_name} ... \r")
            try:
                with transaction.atomic():
                    obj = PreloadData(**opts)
                    sys.stdout.write(
                        f"   - loading {module_name} ... {obj.item_count} items.\n"
                    )
            except LoadListDataError as e:
                sys.stdout.write(style.ERROR(f"ERROR! {e}\n"))

    def _replace_list_data_or_raise_on_duplicate(self, module, opts: dict) -> None:
        """Raises on duplicates or replaces.

        1. Checks `list model` has not been registered from another app
        2. Updates the list of `list models` already registered.
        3. If duplicate is found raises OR replaces.

        Note: * edc_* modules should load first.
              * only edc_* modules can provide defaults
        """
        models = []
        for label_lower, data in opts.get(self.module_name).items():
            default_module_name = self._get_default_module_name(module, label_lower)
            if label_lower not in self.models:
                models.append(label_lower)
            elif (
                label_lower in self.models
                and default_module_name
                and module.__name__ != default_module_name
            ):
                self._replace_default_list_data_for_model(
                    label_lower, module.__name__, default_module_name
                )
            else:
                raise AlreadyRegistered(
                    "List data for table is already registered. "
                    f"Got table {label_lower} in {module.__name__}."
                )
        self.models.extend(models)

    def _get_default_module_name(self, module, label_lower: str) -> str:
        for full_module_name, opts in self.registry.items():
            if label_lower in (opts.get(self.module_name) or {}):
                for prefix in self.default_module_prefixes:
                    if (
                        full_module_name.startswith(prefix)
                        and full_module_name != module.__name__
                    ):
                        return full_module_name
        return ""

    def _replace_default_list_data_for_model(
        self, label_lower: str, full_module_name: str, default_module_name: str
    ) -> None:
        self.registry[default_module_name][self.module_name].pop(label_lower)
        sys.stdout.write(
            f"   - {self.module_name} from `{full_module_name}.{label_lower}`\n"
            f"       has replaced `{default_module_name}.{label_lower}`.\n"
        )

    @staticmethod
    def _get_options(module) -> dict:
        opts: dict = {}
        opts.update(list_data=getattr(module, "list_data", None))
        opts.update(model_data=getattr(module, "model_data", None))
        opts.update(list_data_model_name=getattr(module, "list_data_model_name", None))
        opts.update(apps=getattr(module, "apps", None))
        if not any([x for x in opts.values()]):
            raise SiteListDataError(f"Invalid list_data module. See {module}")
        return opts

    def autodiscover(self) -> None:
        if (
            get_autodiscover_enabled()
            and "makemigrations" not in sys.argv
            and "showmigrations" not in sys.argv
        ):
            sys.stdout.write(f" * checking sites for `{self.module_name}` ...\n")
            for app_name in django_apps.app_configs:
                try:
                    self._import_and_register(app_name)
                except ModuleNotFoundError:
                    pass

    def _import_and_register(self, app_name: str) -> None:
        import_module(app_name)
        before_import_registry = copy.deepcopy(site_list_data.registry)
        try:
            module = import_module(f"{app_name}.{self.module_name}")
        except Exception as e:
            site_list_data.registry = before_import_registry
            if f"No module named '{app_name}.{self.module_name}'" not in str(e):
                raise SiteListDataError(f"{e} See {app_name}.{self.module_name}")
            else:
                raise
        else:
            self.register(module, app_name=app_name)


site_list_data = SiteListData()
