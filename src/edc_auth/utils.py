from __future__ import annotations

from pprint import pprint
from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from .constants import ACCOUNT_MANAGER_ROLE

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, User

    from .models import Role


def get_user(username: str) -> User | None:
    try:
        user = get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
        user = None
    return user


def compare_codenames_for_group(group_name: str = None, expected: list[str] = None) -> None:
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


def make_view_only_group_permissions(
    prefix: str = None, group: Group = None, model: str = None
):
    """Remove all but view permissions for model.

    Accepts a prefix as well, e.g. `historical`.

    Default removes all except `view`.
    """

    opts = dict(codename__contains=f"_{prefix}")
    if model:
        opts.update(model=model)
    for permission in group.permissions.filter(**opts).exclude(
        codename__startswith=f"view_{prefix}"
    ):
        group.permissions.remove(permission)


def get_codenames_for_role(role_name: str) -> list[str]:
    codenames = []
    role_cls = django_apps.get_model("edc_auth.role")
    try:
        roles = role_cls.objects.get(name=role_name).groups.all()
    except ObjectDoesNotExist:
        pass
    else:
        for group in roles:
            codenames.extend(
                [
                    f"{permission.content_type.app_label}.{permission.codename}"
                    for permission in group.permissions.all()
                ]
            )
    return codenames


def user_has_change_perms(**kwargs) -> list[str]:
    codenames = get_codenames_for_user(**kwargs)
    return [c for c in codenames if "add_" in c or "change_" in c or "delete_" in c]


def get_codenames_for_user(
    user: User = None, roles: QuerySet[Role] = None, include_groups: bool | None = None
) -> list[str]:
    codenames: list[str] = []
    groups: list[Group] = []
    account_manager_groups: list[Group] = []
    try:
        role: Role = django_apps.get_model("edc_auth.role").objects.get(
            name=ACCOUNT_MANAGER_ROLE
        )
    except ObjectDoesNotExist:
        pass
    else:
        account_manager_groups: list[Group] = [grp for grp in role.groups.all()]
    roles = roles or user.userprofile.roles

    for role in roles.all():
        groups.extend([grp for grp in role.groups.all() if grp not in account_manager_groups])
    if include_groups:
        for group in user.groups.all():
            if group not in account_manager_groups:
                groups.append(group)
    groups = list(set(groups))
    for group in groups:
        codenames.extend(
            [
                f"{permission.content_type.app_label}.{permission.codename}"
                for permission in group.permissions.all()
            ]
        )
    codenames.extend(
        [
            f"{permission.content_type.app_label}.{permission.codename}"
            for permission in user.user_permissions.all()
        ]
    )
    return codenames
