import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style


style = color_style()


def update_roles(groups_by_role_name=None, role_names=None, verbose=None):
    """Updates or creates role model instances.

    Role model instances refer to group instances. If a group by name
    does not exist, it will be created.

    Group permissions are added later using the GroupPermissionsUpdater.
    Group permissions are usually edc specific and the
    GroupPermissionsUpdater is usually callled from your main edc app.
    """
    if verbose:
        sys.stdout.write(style.MIGRATE_HEADING("Updating roles:\n"))
    role_model_cls = django_apps.get_model("edc_auth.role")
    group_model_cls = django_apps.get_model("auth.group")
    index = 0
    for role_name, groups in groups_by_role_name.items():
        if verbose:
            sys.stdout.write(f" * updating groups for {role_names.get(role_name)}.\n")
        try:
            role = role_model_cls.objects.get(name=role_name)
        except ObjectDoesNotExist:
            role = role_model_cls.objects.create(
                name=role_name,
                display_name=role_names.get(role_name),
                display_index=index,
            )
        role.display_name = role_names.get(role_name)
        role.display_index = index
        role.save()
        role.groups.clear()
        for group_name in groups:
            try:
                group = group_model_cls.objects.get(name=group_name)
            except ObjectDoesNotExist:
                group = group_model_cls.objects.create(name=group_name)
            role.groups.add(group)
        index += 1
    if verbose:
        sys.stdout.write("Done.\n")
        sys.stdout.flush()
