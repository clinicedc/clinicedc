from __future__ import annotations

import sys
from copy import deepcopy
from typing import Any

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class AlreadyRegistered(Exception):
    pass


class SiteValuesMappingError(Exception):
    pass


class SiteValuesMappings:

    """
    # values_mappings.py
    import string

    from edc_pdutils.site_values_mappings import site_values_mappings

    from . import choices

    for attr in dir(choices):
        if attr[0] in string.ascii_uppercase:
            value = getattr(choices, attr)
            if isinstance(value, tuple):
                site_values_mappings.register(attr, getattr(choices, attr))

    """

    def __init__(self):
        self.registry = {}
        self.loaded = False

    def register(
        self,
        name: str = None,
        choices: tuple[tuple[str, Any]] = None,
        values_mapping: tuple[tuple[int, Any]] | None = None,
    ):
        if name in self.registry:
            raise AlreadyRegistered(f"Values mapping already registered. Got {name}.")
        if not values_mapping:
            values_mapping = self.generate_values_mapping(choices)
        self.registry.update({name: [choices, values_mapping]})
        self.loaded = True

    @staticmethod
    def generate_values_mapping(choices: tuple[tuple[str, Any]]) -> tuple[tuple[int, str]]:
        values_mapping = []
        for index, choice in enumerate(choices):
            try:
                values_mapping.append((index, str(choice[1][::79])))
            except IndexError as e:
                raise IndexError(f"{str(e)} Got {choice[1]}")
        return tuple(values_mapping)

    def get_by_choices(self, tpl: tuple[tuple[str, Any]]) -> tuple[tuple[int, str]] | None:
        for data in self.registry.values():
            if data[0] == tpl:
                return data[1]
        return None

    @staticmethod
    def autodiscover(module_name=None, verbose=True):
        """Autodiscovers values_mappings in the values_mappings.py file of
        any INSTALLED_APP.
        """
        before_import_registry = None
        module_name = module_name or "values_mappings"
        writer = sys.stdout.write if verbose else lambda x: x
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = deepcopy(site_values_mappings.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered values mapping '{module_name}' from '{app}'\n")
                except ImportError as e:
                    site_values_mappings.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteValuesMappingError(f"{str(e)}. See {app}.{module_name}")
            except ImportError:
                pass


site_values_mappings = SiteValuesMappings()
