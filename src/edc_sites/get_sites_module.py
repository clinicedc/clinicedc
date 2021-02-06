from importlib import import_module
from warnings import warn

from django.conf import settings
from django.core.management.color import color_style

style = color_style()


def get_sites_module():
    default_module_name = "edc_sites.sites"
    sites_module_name = getattr(settings, "EDC_SITES_MODULE_NAME", default_module_name)
    if default_module_name == sites_module_name:
        warn(style.NOTICE(f"Using default sites module. `{default_module_name}`."))
    return import_module(sites_module_name or default_module_name)
