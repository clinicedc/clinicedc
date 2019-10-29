import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.core.checks.registry import register
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from django.db.models.signals import post_migrate
from warnings import warn

from .role_names import role_names, groups_by_role_name
from .system_checks import edc_check


style = color_style()


def post_migrate_user_roles(sender=None, **kwargs):
    sys.stdout.write(style.MIGRATE_HEADING("Updating roles:\n"))
    Role = django_apps.get_model("edc_auth.role")
    Group = django_apps.get_model("auth.group")
    index = 0
    for role_name, groups in groups_by_role_name.items():
        sys.stdout.write(
            f" * updating groups for {role_names.get(role_name)}.\n")
        try:
            role = Role.objects.get(name=role_name)
        except ObjectDoesNotExist as e:
            role = Role.objects.create(
                name=role_name,
                display_name=role_names.get(role_name),
                display_index=index)
        else:
            role.groups.clear()
            for group_name in groups:
                try:
                    role.groups.add(Group.objects.get(name=group_name))
                except ObjectDoesNotExist as e:
                    warn(f"Group {group_name} not found. Got {e}\n")
        index += 1
    sys.stdout.write("Done.\n")
    sys.stdout.flush()


class AppConfig(DjangoAppConfig):
    name = "edc_auth"
    verbose_name = "Edc Authentication"

    def ready(self):
        from .signals import (
            update_user_profile_on_post_save,
            update_user_groups_on_role_m2m_changed,
        )

        register(edc_check)
        post_migrate.connect(post_migrate_user_roles, sender=self)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
