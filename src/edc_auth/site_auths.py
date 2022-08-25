import sys
from copy import deepcopy
from typing import Callable, Tuple

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.module_loading import import_module, module_has_submodule

from .auth_objects import default_groups, default_pii_models, default_roles


class AlreadyRegistered(Exception):
    pass


class InvalidGroup(Exception):
    pass


class InvalidRole(Exception):
    pass


class RoleAlreadyExists(Exception):
    pass


class GroupAlreadyExists(Exception):
    pass


class PiiModelAlreadyExists(Exception):
    pass


class SiteAuthError(Exception):
    pass


def is_view_codename(codename):
    return (
        "view_" in codename
        or "view_historical" in codename
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
            "groups": default_groups,
            "roles": default_roles,
            "update_groups": {},
            "update_roles": {},
            "custom_permissions_tuples": {},
            "pre_update_funcs": [],
            "post_update_funcs": [],
            "pii_models": default_pii_models,
        }

    def clear(self):
        self.registry = {
            "groups": {},
            "roles": {},
            "update_groups": {},
            "update_roles": {},
            "custom_permissions_tuples": {},
            "pre_update_funcs": [],
            "post_update_funcs": [],
            "pii_models": [],
        }

    def clear_values(self):
        registry = deepcopy(self.registry)
        self.registry = {
            "groups": {k: [] for k in registry.get("groups")},
            "roles": {k: [] for k in self.registry.get("roles")},
            "update_groups": {},
            "update_roles": {},
            "custom_permissions_tuples": {},
            "pre_update_funcs": [],
            "post_update_funcs": [],
            "pii_models": [],
        }

    @property
    def edc_auth_skip_site_auths(self):
        return getattr(settings, "EDC_AUTH_SKIP_SITE_AUTHS", False)

    def add_pre_update_func(self, func):
        self.registry["pre_update_funcs"].append(func)

    def add_post_update_func(self, app_label: str, func: Callable):
        self.registry["post_update_funcs"].append((app_label, func))

    def add_pii_model(self, model_name):
        if model_name in self.registry["pii_models"]:
            raise PiiModelAlreadyExists(f"PII model already exists. Got {model_name}")
        self.registry["pii_models"].append(model_name)

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
        if name in self.registry["groups"]:
            raise GroupAlreadyExists(f"Group name already exists. Got {name}.")
        if no_delete:
            codenames_or_func = self.remove_delete_codenames(codenames_or_func)
        if view_only:
            codenames_or_func = self.get_view_only_codenames(codenames_or_func)
        if convert_to_export:
            codenames_or_func = self.convert_to_export_codenames(codenames_or_func)
        self.registry["groups"].update({name: codenames_or_func})

    def add_role(self, *group_names, name=None):
        if name in self.registry["roles"]:
            raise RoleAlreadyExists(f"Role name already exists. Got {name}.")
        group_names = list(set(group_names))
        self.registry["roles"].update({name: group_names})

    def update_group(
        self, *codenames_or_func, name=None, key=None, view_only=None, no_delete=None
    ) -> None:
        key = key or "update_groups"
        if no_delete:
            codenames_or_func = self.remove_delete_codenames(codenames_or_func)
        if view_only:
            codenames_or_func = self.get_view_only_codenames(codenames_or_func)
        codenames_or_func = list(set(codenames_or_func))
        existing_codenames = deepcopy(self.registry[key].get(name)) or []
        try:
            existing_codenames = list(set(existing_codenames))
        except TypeError as e:
            raise TypeError(f"{e}. Got {name}")
        existing_codenames.extend(codenames_or_func)
        existing_codenames = list(set(existing_codenames))
        self.registry[key].update({name: existing_codenames})

    def update_role(self, *group_names, name=None, key=None) -> None:
        key = key or "update_roles"
        group_names = list(set(group_names))
        existing_group_names = deepcopy(self.registry[key].get(name)) or []
        existing_group_names = list(set(existing_group_names))
        existing_group_names.extend(group_names)
        existing_group_names = list(set(existing_group_names))
        self.registry[key].update({name: existing_group_names})

    def add_custom_permissions_tuples(
        self, model: str, codename_tuples: Tuple[Tuple[str, str], ...]
    ):
        try:
            self.registry["custom_permissions_tuples"][model]
        except KeyError:
            self.registry["custom_permissions_tuples"].update({model: []})
        for codename_tuple in codename_tuples:
            if codename_tuple not in self.registry["custom_permissions_tuples"][model]:
                self.registry["custom_permissions_tuples"][model].append(codename_tuple)

    @staticmethod
    def get_view_only_codenames(codenames):
        """Returns a list of view only codenames.

        If codename is a callable, wraps for a later call.

        Does not remove `edc_navbar` and `edc_dashboard` codenames.
        """
        callables = [lambda: view_only_wrapper(c) for c in codenames if callable(c)]
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
        return self.registry["roles"]

    @property
    def groups(self):
        return self.registry["groups"]

    @property
    def pii_models(self):
        return self.registry["pii_models"]

    @property
    def pre_update_funcs(self):
        return self.registry["pre_update_funcs"]

    @property
    def post_update_funcs(self) -> Tuple[str, Callable]:
        return self.registry["post_update_funcs"]

    @property
    def custom_permissions_tuples(self):
        return self.registry["custom_permissions_tuples"]

    def verify_and_populate(self):
        """Verifies that updates refer to existing group
        or roles names.

        * Updates data from `update_groups` -> `groups`
        * Updates data from `update_roles` -> `roles`
        """
        for name, codenames in self.registry["update_groups"].items():
            if name not in self.registry["groups"]:
                raise InvalidGroup(
                    f"Cannot update group. Group name does not exist. Got {name}."
                )
            self.update_group(*codenames, name=name, key="groups")
        for name, group_names in self.registry["update_roles"].items():
            if name not in self.registry["roles"]:
                raise InvalidRole(f"Cannot update role. Role name does not exist. Got {name}.")
            self.update_role(*group_names, name=name, key="roles")

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers in the auths.py file of any INSTALLED_APP."""
        if not self.edc_auth_skip_site_auths:
            before_import_registry = None
            module_name = module_name or "auths"
            writer = sys.stdout.write if verbose else lambda x: x
            writer(f" * checking for site {module_name} ...\n")
            for app in django_apps.app_configs:
                writer(f" * searching {app}           \r")
                try:
                    mod = import_module(app)
                    try:
                        before_import_registry = deepcopy(site_auths.registry)
                        import_module(f"{app}.{module_name}")
                        writer(f" * registered '{module_name}' from '{app}'\n")
                    except ImportError as e:
                        site_auths.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise SiteAuthError(str(e))
                except ImportError:
                    pass
            self.verify_and_populate()


site_auths = SiteAuths()
