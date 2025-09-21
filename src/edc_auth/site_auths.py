from __future__ import annotations

import sys
from collections.abc import Callable
from copy import deepcopy
from warnings import warn

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.module_loading import import_module, module_has_submodule

from .auth_objects import default_pii_models, get_default_groups, get_default_roles
from .constants import (
    CUSTOM_PERMISSIONS_TUPLES_KEY,
    GROUPS_KEY,
    PII_MODELS_KEY,
    POST_UPDATE_FUNCS_KEY,
    PRE_UPDATE_FUNCS_KEY,
    ROLES_KEY,
    UPDATE_GROUPS_KEY,
    UPDATE_ROLES_KEY,
)


class AlreadyRegistered(Exception):  # noqa: N818
    pass


class InvalidGroup(Exception):  # noqa: N818
    pass


class InvalidRole(Exception):  # noqa: N818
    pass


class RoleAlreadyExists(Exception):  # noqa: N818
    pass


class GroupAlreadyExists(Exception):  # noqa: N818
    pass


class PiiModelAlreadyExists(Exception):  # noqa: N818
    pass


class SiteAuthError(Exception):
    pass


def is_view_codename(codename):
    return (
        "view_" in codename
        or "view_historical" in codename
        or "nav_" in codename
        or "navbar" in codename
        or "dashboard" in codename
    )


def view_only_wrapper(func):
    codenames = func()
    return [codename for codename in codenames if is_view_codename(codename)]


def convert_view_to_export_wrapper(codename_or_callables):
    codenames = []
    export_codenames = []
    for codename in codename_or_callables:
        try:
            codenames.extend(codename())
        except TypeError:
            codenames.append(codename)
    for codename in codenames:
        if is_view_codename(codename) and "historical" not in codename:
            try:
                django_apps.get_model(codename.replace("view_", ""))
            except LookupError:
                pass
            else:
                export_codenames.append(codename.replace("view_", "export_"))
    return export_codenames


def remove_delete_wrapper(codename_or_callables):
    codenames = []
    for codename in codename_or_callables:
        try:
            codenames.extend(codename())
        except TypeError:
            codenames.append(codename)
    return [c for c in codenames if "delete_" not in c]


class SiteAuths:
    """A global to hold the intended group and role data.

    Data will be used by `AuthUpdater`.
    """

    def __init__(self):
        self.registry = {}
        self.initialize()

    def initialize(self):
        self.registry = {
            GROUPS_KEY: get_default_groups(),
            ROLES_KEY: get_default_roles(),
            UPDATE_GROUPS_KEY: {},
            UPDATE_ROLES_KEY: {},
            CUSTOM_PERMISSIONS_TUPLES_KEY: {},
            PRE_UPDATE_FUNCS_KEY: [],
            POST_UPDATE_FUNCS_KEY: [],
            PII_MODELS_KEY: default_pii_models,
        }

    def clear(self):
        self.registry = {
            GROUPS_KEY: {},
            ROLES_KEY: {},
            UPDATE_GROUPS_KEY: {},
            UPDATE_ROLES_KEY: {},
            CUSTOM_PERMISSIONS_TUPLES_KEY: {},
            PRE_UPDATE_FUNCS_KEY: [],
            POST_UPDATE_FUNCS_KEY: [],
            PII_MODELS_KEY: [],
        }

    def clear_values(self):
        registry = deepcopy(self.registry)
        self.registry = {
            GROUPS_KEY: {k: [] for k in registry.get(GROUPS_KEY)},
            ROLES_KEY: {k: [] for k in self.registry.get(ROLES_KEY)},
            UPDATE_GROUPS_KEY: {},
            UPDATE_ROLES_KEY: {},
            CUSTOM_PERMISSIONS_TUPLES_KEY: {},
            PRE_UPDATE_FUNCS_KEY: [],
            POST_UPDATE_FUNCS_KEY: [],
            PII_MODELS_KEY: [],
        }

    @property
    def edc_auth_skip_site_auths(self):
        return getattr(settings, "EDC_AUTH_SKIP_SITE_AUTHS", False)

    def add_pre_update_func(self, func):
        self.registry[PRE_UPDATE_FUNCS_KEY].append(func)

    def add_post_update_func(self, app_label: str, func: Callable):
        self.registry[POST_UPDATE_FUNCS_KEY].append((app_label, func))

    def add_pii_model(self, model_name):
        if model_name in self.registry[PII_MODELS_KEY]:
            raise PiiModelAlreadyExists(f"PII model already exists. Got {model_name}")
        self.registry[PII_MODELS_KEY].append(model_name)

    def add_groups(self, data: dict):
        for name, codenames in data.items():
            self.add_group(codenames, name=name)

    def add_roles(self, data: dict):
        for name, group_names in data.items():
            self.add_role(group_names, name=name)

    def add_group(
        self,
        *codenames_or_func,
        name=None,
        view_only=None,
        convert_to_export=None,
        no_delete=None,
    ):
        if name in self.registry[GROUPS_KEY]:
            raise GroupAlreadyExists(f"Group name already exists. Got {name}.")
        if no_delete:
            codenames_or_func = self.remove_delete_codenames(codenames_or_func)
        if view_only:
            codenames_or_func = self.get_view_only_codenames(codenames_or_func)
        if convert_to_export:
            codenames_or_func = self.convert_to_export_codenames(codenames_or_func)
        self.registry[GROUPS_KEY].update({name: codenames_or_func})

    def add_role(self, *group_names, name=None):
        if name in self.registry[ROLES_KEY]:
            raise RoleAlreadyExists(f"Role name already exists. Got {name}.")
        group_names = list(set(group_names))
        self.registry[ROLES_KEY].update({name: group_names})

    def update_group(
        self, *codenames_or_func, name=None, key=None, view_only=None, no_delete=None
    ) -> None:
        key = key or UPDATE_GROUPS_KEY
        if no_delete:
            codenames_or_func = self.remove_delete_codenames(codenames_or_func)
        if view_only:
            codenames_or_func = self.get_view_only_codenames(codenames_or_func)
        codenames_or_func = list(set(codenames_or_func))
        existing_codenames = deepcopy(self.registry[key].get(name)) or []
        try:
            existing_codenames = list(set(existing_codenames))
        except TypeError as e:
            raise TypeError(f"{e}. Got {name}") from e
        existing_codenames.extend(codenames_or_func)
        existing_codenames = list(set(existing_codenames))
        self.registry[key].update({name: existing_codenames})

    def update_role(self, *group_names, name=None, key=None) -> None:
        key = key or UPDATE_ROLES_KEY
        group_names = list(set(group_names))
        existing_group_names = [
            name for name in self.registry[key].get(name) or [] if name not in group_names
        ]
        existing_group_names.extend(group_names)
        self.registry[key].update({name: existing_group_names})

    def add_custom_permissions_tuples(
        self, model: str, codename_tuples: tuple[tuple[str, str], ...]
    ):
        try:
            self.registry[CUSTOM_PERMISSIONS_TUPLES_KEY][model]
        except KeyError:
            self.registry[CUSTOM_PERMISSIONS_TUPLES_KEY].update({model: []})
        for codename_tuple in codename_tuples:
            if codename_tuple not in self.registry[CUSTOM_PERMISSIONS_TUPLES_KEY][model]:
                self.registry[CUSTOM_PERMISSIONS_TUPLES_KEY][model].append(codename_tuple)

    @staticmethod
    def get_view_only_codenames(codenames):
        """Returns a list of view only codenames.

        If codename is a callable, wraps for a later call.

        Does not remove `edc_navbar`, 'nav_' or `edc_dashboard`
        codenames.
        """
        # callables = [lambda: view_only_wrapper(c) for c in codenames if callable(c)]
        callables = [lambda c=c: view_only_wrapper(c) for c in codenames if callable(c)]
        view_only_codenames = [
            codename
            for codename in codenames
            if not callable(codename) and is_view_codename(codename)
        ]
        view_only_codenames.extend(callables)
        return view_only_codenames

    @staticmethod
    def convert_to_export_codenames(codenames):
        """Returns a list of export only codenames by
        replacing `view` codenames with `export`.

        If codename is a callable, wraps for a later call.
        """
        export_codenames = []
        callables = [codename for codename in codenames if callable(codename)]
        codenames = [codename for codename in codenames if not callable(codename)]
        if callables:
            export_codenames.append(lambda: convert_view_to_export_wrapper(callables))
        if codenames:
            export_codenames.extend(convert_view_to_export_wrapper(codenames))
        return export_codenames

    @staticmethod
    def remove_delete_codenames(codenames):
        export_codenames = []
        callables = [codename for codename in codenames if callable(codename)]
        codenames = [codename for codename in codenames if not callable(codename)]
        if callables:
            export_codenames.append(lambda: remove_delete_wrapper(callables))
        if codenames:
            export_codenames.extend(remove_delete_wrapper(codenames))
        return export_codenames

    @property
    def roles(self):
        return self.registry[ROLES_KEY]

    @property
    def groups(self):
        return self.registry[GROUPS_KEY]

    @property
    def pii_models(self):
        return self.registry[PII_MODELS_KEY]

    @property
    def pre_update_funcs(self):
        return self.registry[PRE_UPDATE_FUNCS_KEY]

    @property
    def post_update_funcs(self) -> tuple[str, Callable]:
        return self.registry[POST_UPDATE_FUNCS_KEY]

    @property
    def custom_permissions_tuples(self):
        return self.registry[CUSTOM_PERMISSIONS_TUPLES_KEY]

    def verify_and_populate(
        self, app_name: str | None = None, warn_only: bool | None = None
    ) -> None:
        """Verifies that updates refer to existing group
        or roles names.

        * Updates data from `update_groups` -> `groups`
        * Updates data from `update_roles` -> `roles`
        """
        for name, codenames in self.registry[UPDATE_GROUPS_KEY].items():
            if name not in self.registry[GROUPS_KEY]:
                msg = (
                    f"Cannot update group. Group name does not exist. See app={app_name}"
                    f"update_groups['groups']={codenames}. Got {name}"
                )
                if warn_only:
                    warn(msg, stacklevel=2)
                else:
                    raise InvalidGroup(msg)
            self.update_group(*codenames, name=name, key=GROUPS_KEY)
        self.registry[UPDATE_GROUPS_KEY] = {}
        for name, group_names in self.registry[UPDATE_ROLES_KEY].items():
            if name not in self.registry[ROLES_KEY]:
                msg = (
                    f"Cannot update role. Role name does not exist. See app={app_name}. "
                    f"update_roles['groups']={group_names}. Got {name}"
                )
                if warn_only:
                    warn(msg, stacklevel=2)
                else:
                    raise InvalidRole(msg)
            self.update_role(*group_names, name=name, key=ROLES_KEY)
        self.registry[UPDATE_ROLES_KEY] = {}

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers in the auths.py file of any INSTALLED_APP."""
        if not self.edc_auth_skip_site_auths:
            before_import_registry = None
            module_name = module_name or "auths"
            writer = sys.stdout.write if verbose else lambda x: x
            writer(f" * checking for site {module_name} ...\n")
            for app_name in django_apps.app_configs:
                writer(f" * searching {app_name}           \r")
                try:
                    mod = import_module(app_name)
                    try:
                        before_import_registry = deepcopy(site_auths.registry)
                        import_module(f"{app_name}.{module_name}")
                        writer(f"   - registered '{module_name}' from '{app_name}'\n")
                    except ImportError as e:
                        site_auths.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise SiteAuthError(str(e)) from e
                except ImportError:
                    pass
            self.verify_and_populate(app_name=app_name)


site_auths = SiteAuths()
