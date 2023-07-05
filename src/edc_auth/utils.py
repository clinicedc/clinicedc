from pprint import pprint
from typing import Any

from django.apps import apps as django_apps


def compare_codenames_for_group(group_name=None, expected=None):
    group = django_apps.get_model("auth.group").objects.get(name=group_name)
    codenames = [p.codename for p in group.permissions.all()]
    new_expected = []
    for c in expected:
        try:
            c = c.split(".")[1]
        except IndexError:
            pass
        new_expected.append(c)

    compared = [c for c in new_expected if c not in codenames]
    if compared:
        print(group.name, "missing from codenames")
        pprint(compared)
    compared = [c for c in codenames if c not in new_expected]
    if compared:
        print(group.name, "extra codenames")
        pprint(compared)


def remove_default_model_permissions_from_edc_permissions(auth_updater: Any, app_label: str):
    for group in auth_updater.group_model_cls.objects.all():
        auth_updater.remove_permissions_by_codenames(
            group=group,
            codenames=[
                f"{app_label}.add_edcpermissions",
                f"{app_label}.change_edcpermissions",
                f"{app_label}.delete_edcpermissions",
                f"{app_label}.view_edcpermissions",
            ],
        )


def make_view_only_group_permissions(prefix: str = None, group=None, model=None):
    """Remove all but view permissions for model.

    Accepts a prefix as well, e.g. `historical'.

    Default removes all except `view`.
    """

    opts = dict(codename__contains=f"_{prefix}")
    if model:
        opts.update(model=model)
    for permission in group.permissions.filter(**opts).exclude(
        codename__startswith=f"view_{prefix}"
    ):
        group.permissions.remove(permission)
