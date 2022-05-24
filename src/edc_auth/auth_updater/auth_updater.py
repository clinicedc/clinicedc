import sys
from typing import Optional

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style

from ..site_auths import site_auths
from .group_updater import GroupUpdater
from .role_updater import RoleUpdater

style = color_style()


class AuthUpdater:
    group_updater_cls = GroupUpdater
    role_updater_cls = RoleUpdater

    def __init__(
        self,
        groups: Optional[dict] = None,
        roles: Optional[dict] = None,
        pii_models: Optional[list] = None,
        pre_update_funcs: Optional[list] = None,
        post_update_funcs: Optional[list] = None,
        custom_permissions_tuples: Optional[dict] = None,
        verbose=None,
        apps=None,
        warn_only=None,
    ):
        site_auths.verify_and_populate()
        custom_permissions_tuples = (
            custom_permissions_tuples or site_auths.custom_permissions_tuples
        )
        groups = groups or site_auths.groups
        pii_models = pii_models or site_auths.pii_models
        post_update_funcs = post_update_funcs or site_auths.post_update_funcs
        pre_update_funcs = pre_update_funcs or site_auths.pre_update_funcs
        roles = roles or site_auths.roles
        self.apps = apps
        if not self.edc_auth_skip_auth_updater:
            self.verbose = verbose
            self.apps = apps
            if self.verbose:
                sys.stdout.write(style.MIGRATE_HEADING("Updating groups and permissions:\n"))
            self.group_updater = self.group_updater_cls(
                groups=groups,
                pii_models=pii_models,
                custom_permissions_tuples=custom_permissions_tuples,
                verbose=self.verbose,
                apps=self.apps,
                warn_only=warn_only,
            )
            self.role_updater = self.role_updater_cls(
                roles=roles,
                verbose=self.verbose,
            )
            self.run_pre_updates(pre_update_funcs)
            self.group_updater.create_custom_permissions_from_tuples()
            self.groups = self.group_updater.update_groups()
            self.roles = self.role_updater.update_roles()
            self.run_post_updates(post_update_funcs)
            self.refresh_groups_in_roles_per_user()
            if verbose:
                sys.stdout.write(style.MIGRATE_HEADING("Done.\n"))
                sys.stdout.flush()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(edc_auth_skip_auth_updater="
            f"{self.edc_auth_skip_auth_updater})"
        )

    @property
    def edc_auth_skip_auth_updater(self):
        return getattr(settings, "EDC_AUTH_SKIP_AUTH_UPDATER", False)

    def run_pre_updates(self, pre_updates):
        """Custom funcs that operate after all groups and roles have been created"""
        if self.verbose:
            sys.stdout.write(style.MIGRATE_HEADING(" - Running pre updates:\n"))
        if pre_updates:
            for func in pre_updates:
                sys.stdout.write(f"   * {func.__name__}\n")
                func(self)
        else:
            if self.verbose:
                sys.stdout.write("   * nothing to do\n")
        if self.verbose:
            sys.stdout.write("   Done.\n")

    def run_post_updates(self, post_updates):
        """Custom funcs that operate after all groups and roles have been created"""
        if self.verbose:
            sys.stdout.write(style.MIGRATE_HEADING(" - Running post updates:\n"))
        if post_updates:
            for func in post_updates:
                sys.stdout.write(f"   * {func.__name__}\n")
                func(self)
        else:
            if self.verbose:
                sys.stdout.write("   * nothing to do\n")
        if self.verbose:
            sys.stdout.write("   Done.\n")

    def create_permissions_from_tuples(self, **kwargs):
        return self.group_updater.create_permissions_from_tuples(**kwargs)

    @property
    def group_model_cls(self):
        return self.group_updater.group_model_cls

    def remove_permissions_by_codenames(self, **kwargs):
        return self.group_updater.remove_permissions_by_codenames(**kwargs)

    @classmethod
    def add_empty_groups_for_tests(cls, *extra_names, apps=None):
        """Adds group names without codenames.

        For tests
        """
        apps = apps or django_apps
        groups_names = extra_names + tuple(site_auths.groups)
        for name in groups_names:
            try:
                apps.get_model("auth.group").objects.get(name=name)
            except ObjectDoesNotExist:
                apps.get_model("auth.group").objects.create(name=name)
                site_auths.groups.update({name: []})
        return groups_names

    @classmethod
    def add_empty_roles_for_tests(cls, *extra_names, apps=None):
        """Adds roles names without groups.

        For tests
        """
        apps = apps or django_apps
        role_names = extra_names + tuple(site_auths.roles)
        for name in role_names:
            display_name = name.replace("_", " ").lower().title()
            try:
                role_obj = apps.get_model("edc_auth.role").objects.get(name=name)
            except ObjectDoesNotExist:
                apps.get_model("edc_auth.role").objects.create(
                    name=name, display_name=display_name
                )
                site_auths.roles.update({name: []})
            else:
                role_obj.display_name = display_name
                role_obj.save()
        return role_names

    @staticmethod
    def refresh_groups_in_roles_per_user():
        """Clear then add back roles to trigger post-save signal."""
        for user in get_user_model().objects.all():
            roles = [obj for obj in user.userprofile.roles.all()]
            user.userprofile.roles.clear()
            user.groups.clear()
            for role in roles:
                user.userprofile.roles.add(role)
            user.userprofile.save()
            user.save()
