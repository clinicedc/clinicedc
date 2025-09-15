from __future__ import annotations

import copy
import sys
from collections.abc import Callable
from importlib import import_module
from typing import Any

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule


class AlreadyRegistered(Exception):
    pass


class SitePharmacyError(Exception):
    pass


class LabelConfig:
    def __init__(
        self,
        name: str,
        drawing_callable: Callable,
        label_cls: Any,
        test_data_func: Callable | None = None,
    ):
        self.name = name
        self.drawing_callable = drawing_callable
        self.label_cls = label_cls
        self.test_data_func = test_data_func or self._test_data_func

    def _test_data_func(self) -> dict:
        return {}

    def __repr__(self):
        return self.__class__.__name__ + f"({self.name})"

    def __str__(self):
        return self.__class__.__name__ + f"({self.name})"


class SiteLabelConfigs:
    def __init__(self):
        self.registry: dict[str, LabelConfig] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __len__(self):
        return len(self.registry.values())

    def __iter__(self):
        return iter(self.registry.values())

    def unregister(self, key) -> None:
        if key in self.registry:
            del self.registry[key]

    def register(
        self,
        name: str,
        drawing_callable: Callable,
        label_cls: Any,
        test_data_func: Callable | None = None,
    ) -> None:
        if name in self.registry:
            raise AlreadyRegistered(f"Already registered. Got name='{name}' ")
        self.registry.update(
            {name: LabelConfig(name, drawing_callable, label_cls, test_data_func)}
        )

    def all(self) -> dict[str, LabelConfig]:
        return self.registry

    def get(self, name) -> LabelConfig:
        if name not in self.registry:
            raise SitePharmacyError(
                f"Name does not exist. Is it registered? "
                f"Expected one of {self.registry}. Got {name}."
            )
        return self.registry.get(name)

    @staticmethod
    def autodiscover(module_name=None, verbose=True):
        before_import_registry = {}
        module_name = module_name or "label_configs"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_label_configs.registry)
                    import_module(f"{app}.{module_name}")
                    writer(f"   - registered '{module_name}' from '{app}'\n")
                except SitePharmacyError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_label_configs.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SitePharmacyError(str(e))
            except ImportError:
                pass


site_label_configs = SiteLabelConfigs()
