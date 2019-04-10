import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule
from importlib import import_module

from .preload_data import PreloadDataError


class SiteListDataError(Exception):
    pass


class SiteListData:

    """Load list data from any module named "list_data".

    Called in AppConfig or by management command.
    """

    def autodiscover(self, module_name=None, verbose=True):
        if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
            module_name = module_name or "list_data"
            writer = sys.stdout.write if verbose else lambda x: x
            style = color_style()
            writer(f" * checking for site {module_name} ...\n")
            for app in django_apps.app_configs:
                writer(f" * searching {app}           \r")
                try:
                    mod = import_module(app)
                    try:
                        import_module(f"{app}.{module_name}")
                        writer(f" * loading '{module_name}' from '{app}'\n")
                    except PreloadDataError as e:
                        writer(f"   - loading {app}.{module_name} ... ")
                        writer(style.ERROR(f"ERROR! {e}\n"))
                    except ImportError as e:
                        if module_has_submodule(mod, module_name):
                            raise SiteListDataError(e)
                except ImportError:
                    pass


site_list_data = SiteListData()
