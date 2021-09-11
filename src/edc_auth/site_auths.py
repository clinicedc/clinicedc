import sys
from copy import deepcopy

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.module_loading import import_module, module_has_submodule

from .default_groups import default_groups
from .default_pii_models import default_pii_models
from .default_roles import default_roles

edc_auth_skip_site_auths = getattr(settings, "EDC_AUTH_SKIP_SITE_AUTHS", False)


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


class SiteAuths:
    """A global to hold the intended group and role data.

    Data will be used by AuthUpdater.
    """

    def __init__(self):
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

    def add_pre_update_func(self, func):
        self.registry["pre_update_funcs"].append(func)

    def add_post_update_func(self, func):
        self.registry["post_update_funcs"].append(func)

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

    def add_group(self, *codenames_or_func, name=None):
        if name in self.registry["groups"]:
            raise GroupAlreadyExists(f"Group name already exists. Got {name}.")
        self.registry["groups"].update({name: codenames_or_func})

    def add_role(self, *group_names, name=None):
        if name in self.registry["roles"]:
            raise RoleAlreadyExists(f"Role name already exists. Got {name}.")
        group_names = list(set(group_names))
        self.registry["roles"].update({name: group_names})

    def update_group(self, *codenames, name=None, key=None) -> None:
        key = key or "update_groups"
        codenames = list(set(codenames))
        existing_codenames = deepcopy(self.registry[key].get(name)) or []
        existing_codenames.extend(codenames)
        existing_codenames = list(set(existing_codenames))
        self.registry[key].update({name: existing_codenames})

    def update_role(self, *group_names, name=None, key=None) -> None:
        key = key or "update_roles"
        group_names = list(set(group_names))
        existing_group_names = deepcopy(self.registry[key].get(name)) or []
        existing_group_names.extend(group_names)
        existing_group_names = list(set(existing_group_names))
        self.registry[key].update({name: existing_group_names})

    def add_custom_permissions_tuples(self, model: str, codename_tuples: tuple):
        try:
            self.registry["custom_permissions_tuples"][model]
        except KeyError:
            self.registry["custom_permissions_tuples"].update({model: []})
        for codename_tuple in codename_tuples:
            if codename_tuple not in self.registry["custom_permissions_tuples"][model]:
                self.registry["custom_permissions_tuples"][model].append(codename_tuple)

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
    def post_update_funcs(self):
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
                raise InvalidRole(
                    f"Cannot update role. Role name does not exist. Got {name}."
                )
            self.update_role(*group_names, name=name, key="roles")

    def autodiscover(self, module_name=None, verbose=True):
        """Autodiscovers in the auths.py file of any INSTALLED_APP."""
        if not edc_auth_skip_site_auths:
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
