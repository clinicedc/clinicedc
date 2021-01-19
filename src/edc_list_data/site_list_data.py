import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.db import transaction
from django.utils.module_loading import module_has_submodule
from importlib import import_module

from .load_list_data import LoadListDataError
from .preload_data import PreloadData


class SiteListDataError(Exception):
    pass


class SiteListData:

    """Load list data from any module named "list_data".

    Called in AppConfig or by management command.
    """

    def autodiscover(self, module_name=None, verbose=True):
        if (
            # "migrate" not in sys.argv
            "makemigrations" not in sys.argv
            and "showmigrations" not in sys.argv
        ):
            module_name = module_name or "list_data"
            writer = sys.stdout.write if verbose else lambda x: x
            style = color_style()
            writer(f"\n * checking for site {module_name} ...\n")
            for app in django_apps.app_configs:
                writer(f" * searching {app}           \r")
                try:
                    mod = import_module(app)
                    try:
                        module = import_module(f"{app}.{module_name}")
                        opts = self.get_options(module)
                        with transaction.atomic():
                            PreloadData(**opts)
                        writer(f" * loading '{module_name}' from '{app}'\n")
                    except LoadListDataError as e:
                        writer(f"   - loading {app}.{module_name} ... \n")
                        writer(style.ERROR(f"ERROR! {e}\n"))
                    except ImportError as e:
                        if module_has_submodule(mod, module_name):
                            raise SiteListDataError(e)
                except ImportError:
                    pass
            writer("\n")

    @staticmethod
    def get_options(module):
        opts = {}
        opts.update(list_data=getattr(module, "list_data", None))
        opts.update(model_data=getattr(module, "model_data", None))
        opts.update(unique_field_data=getattr(module, "unique_field_data", None))
        opts.update(list_data_model_name=getattr(module, "list_data_model_name", None))
        opts.update(apps=getattr(module, "apps", None))
        if not any([x for x in opts.values()]):
            raise SiteListDataError(f"Invalid list_data module. See {module}")
        return opts


site_list_data = SiteListData()
