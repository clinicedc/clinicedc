from importlib import import_module

from django.conf import settings


def get_sites_module():
    default_module_name = "edc_sites.sites"
    sites_module_name = getattr(settings, "EDC_SITES_MODULE_NAME", default_module_name)
    return import_module(sites_module_name or default_module_name)
