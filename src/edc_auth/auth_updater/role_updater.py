import sys
from typing import Optional

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style

style = color_style()


class RoleUpdaterError(Exception):
    pass


class RoleUpdater:
    def __init__(
        self,
        roles: Optional[dict] = None,
        verbose=None,
    ):
        self.roles = roles
        self.verbose = verbose

    @property
    def role_model_cls(self):
        return django_apps.get_model("edc_auth.role")

    @property
    def group_model_cls(self):
        return django_apps.get_model("auth.group")

    def update_roles(self):
        """Updates or creates role model instances.

        Role model instances refer to group instances. If a group by name
        does not exist, it will be created.
        """
        if self.verbose:
            sys.stdout.write(style.MIGRATE_HEADING(" - Updating roles:\n"))
        index = 0
        for role_name, groups in self.roles.items():
            display_name = role_name.replace("_", " ").lower().title()
            if self.verbose:
                sys.stdout.write(f"   * updating groups for {role_name}.\n")
            try:
                role = self.role_model_cls.objects.get(name=role_name)
            except ObjectDoesNotExist:
                role = self.role_model_cls.objects.create(
                    name=role_name,
                    display_name=display_name,
                    display_index=index,
                )
            role.display_name = display_name
            role.display_index = index
            role.save()
            role.groups.clear()
            for group_name in groups:
                try:
                    group = self.group_model_cls.objects.get(name=group_name)
                except ObjectDoesNotExist:
                    raise RoleUpdaterError(
                        "Invalid group specified for role. "
                        f"`{group_name}` is not a group. See role `{role}`."
                    )
                    # group = self.group_model_cls.objects.create(name=group_name)
                role.groups.add(group)
            index += 1
        if self.verbose:
            sys.stdout.write("   Done.\n")
            sys.stdout.flush()
