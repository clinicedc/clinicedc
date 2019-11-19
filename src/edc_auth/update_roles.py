import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from warnings import warn

from .role_names import groups_by_role_name, role_names

style = color_style()


def update_roles(verbose=None):
    if verbose:
        sys.stdout.write(style.MIGRATE_HEADING("Updating roles:\n"))
    Role = django_apps.get_model("edc_auth.role")
    Group = django_apps.get_model("auth.group")
    index = 0
    Role.objects.exclude(name__in=[name for name in groups_by_role_name]).delete()
    for role_name, groups in groups_by_role_name.items():
        if verbose:
            sys.stdout.write(f" * updating groups for {role_names.get(role_name)}.\n")
        try:
            role = Role.objects.get(name=role_name)
        except ObjectDoesNotExist:
            role = Role.objects.create(
                name=role_name,
                display_name=role_names.get(role_name),
                display_index=index,
            )
        else:
            role.display_name = role_names.get(role_name)
            role.display_index = index
            role.save()
            role.groups.clear()
            for group_name in groups:
                try:
                    role.groups.add(Group.objects.get(name=group_name))
                except ObjectDoesNotExist as e:
                    warn(f"Group {group_name} not found. Got {e}\n")
        index += 1
    if verbose:
        sys.stdout.write("Done.\n")
        sys.stdout.flush()
