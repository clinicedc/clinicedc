from __future__ import annotations

import copy
import sys
from importlib import import_module
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from django.urls import NoReverseMatch
from django.utils.module_loading import module_has_submodule

from .exceptions import AlreadyRegistered, NavbarError

if TYPE_CHECKING:
    from .navbar import Navbar


class NavbarCollection:
    """A class to contain a dictionary of navbars. See Navbar."""

    name = "default"

    def __init__(self):
        self.registry = {}
        self.codenames = {}

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def register(self, navbar: Navbar = None):
        if navbar.name not in self.registry:
            self.registry.update({navbar.name: navbar})
            # self.codenames.update(**navbar.codenames)
        else:
            raise AlreadyRegistered(f"Navbar with name {navbar.name} is already registered.")

    def context(self, name=None, selected_item=None):
        """Returns the named navbar in the collection as context."""
        return dict(
            navbar_item_selected=selected_item,
            navbar=self.get_navbar(name=name, selected_item=selected_item),
            navbar_name=name,
        )

    def get_navbar(self, name: str = None, selected_item: str = None) -> Navbar:
        """Returns a selected navbar in the collection."""
        # does the navbar exist?
        try:
            navbar: Navbar = self.registry[name]
        except KeyError:
            raise NavbarError(
                f"Navbar '{name}' does not exist. Expected one of "
                f"{list(self.registry.keys())}. See {self!r}."
            )
        else:
            # does the navbar have items?
            if not navbar.navbar_items:
                raise NavbarError(
                    f"Navbar '{navbar.name}' has no navbar_item. Expected "
                    f"'{selected_item}'. See {self!r}"
                )
            # does the selected item exist?
            if selected_item:
                navbar.set_active(selected_item)
        return navbar

    def show_user_permissions(self, username: str = None, navbar_name: str = None):
        user = django_apps.get_model("auth.user").objects.get(username=username)
        navbar: Navbar = self.registry.get(navbar_name)
        return navbar.show_user_permissions(user=user)

    def show_user_codenames(self, username=None, navbar_name=None):
        user_permissions = self.show_user_permissions(username, navbar_name)
        codenames = []
        for codename in [list(v.keys()) for v in user_permissions.values()]:
            codenames.extend(codename)
        return codenames

    def autodiscover(self, module_name=None, verbose=True):
        if getattr(settings, "EDC_NAVBAR_ENABLED", True):
            module_name = module_name or "navbars"
            writer = sys.stdout.write if verbose else lambda x: x
            style = color_style()
            writer(f" * checking for site {module_name} ...\n")
            for app in django_apps.app_configs:
                try:
                    mod = import_module(app)
                    try:
                        before_import_registry = copy.copy(site_navbars.registry)
                        import_module(f"{app}.{module_name}")
                        writer(f"   - registered navbars '{module_name}' from '{app}'\n")
                    except NavbarError as e:
                        writer(f"   * loading {app}.navbars ... \n")
                        writer(style.ERROR(f"ERROR! {e}\n"))
                    except NoReverseMatch as e:
                        writer(f"   * loading {app}.navbars ... \n")
                        writer(style.ERROR(f"ERROR! {e}\n"))
                        raise
                    except ImportError as e:
                        site_navbars.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise NavbarError(e)
                except ImportError:
                    pass


site_navbars = NavbarCollection()
