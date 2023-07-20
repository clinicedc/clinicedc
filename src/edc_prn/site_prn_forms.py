from __future__ import annotations

import copy
import sys
from copy import deepcopy
from importlib import import_module
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule

if TYPE_CHECKING:
    from edc_prn import Prn


class AlreadyRegistered(Exception):
    pass


class SitePrnFormsError(Exception):
    pass


class PrnFormsCollection:
    def __init__(self):
        self.registry: dict[str, Prn] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __len__(self):
        return len(self.registry.values())

    def __iter__(self):
        return iter(self.registry.values())

    def register(self, prn: Prn = None) -> None:
        if prn.model in self.registry:
            raise AlreadyRegistered(f"PRN form {prn.model} is already registered.")
        else:
            self.registry.update({prn.model: prn})
        self.reorder_registry()

    def unregister(self, prn: Prn = None) -> None:
        if prn.model in self.registry:
            del self.registry[prn.model]

    def reorder_registry(self) -> None:
        keys = [k for k in self.registry]
        keys.sort()
        registry = deepcopy(self.registry)
        self.registry = {k: registry.get(k) for k in keys}

    def autodiscover(
        self, module_name: str | None = None, verbose: bool | None = True
    ) -> None:
        module_name = module_name or "prn_forms"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}                      \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_prn_forms.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered '{module_name}' from '{app}'\n")
                except SitePrnFormsError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_prn_forms.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SitePrnFormsError(str(e))
            except ImportError:
                pass
            except Exception as e:
                raise SitePrnFormsError(
                    f"{e.__class__.__name__} was raised when loading {module_name}. "
                    f"Got {e} See {app}.{module_name}"
                )


site_prn_forms = PrnFormsCollection()
