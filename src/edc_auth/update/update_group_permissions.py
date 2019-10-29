import sys

from django.core.management.color import color_style
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from ..default_codenames_by_group import default_codenames_by_group
from ..group_names import PII, PII_VIEW
from .utils import (
    add_permissions_to_group_by_codenames,
    create_edc_dashboard_permissions,
    create_edc_navbar_permissions,
    create_or_update_groups,
    remove_historical_group_permissions,
    remove_pii_permissions_from_group,
    create_rando_permissions,
    remove_codenames_for_app_labels,
)

style = color_style()


def update_group_permissions(
    codenames_by_group=None,
    verbose=None,
    excluded_app_labels=None,
    attempt_exclude=None,
):
    if verbose:
        sys.stdout.write(style.MIGRATE_HEADING("Updating group permissions:\n"))

    codenames_by_group = codenames_by_group or {}
    codenames_by_group.update(**default_codenames_by_group)

    if attempt_exclude or excluded_app_labels:
        codenames_by_group = remove_codenames_for_app_labels(
            codenames_by_group, excluded_app_labels=excluded_app_labels
        )

    create_or_update_groups(list(codenames_by_group.keys()))
    create_edc_dashboard_permissions()
    create_edc_navbar_permissions()
    create_rando_permissions()

    for group_name, codenames in codenames_by_group.items():
        if verbose:
            sys.stdout.write(f"  * {group_name.lower()}\n")
        try:
            group = Group.objects.get(name=group_name)
        except ObjectDoesNotExist as e:
            raise ObjectDoesNotExist(f"{e} Got {group_name}")

        group.permissions.clear()
        add_permissions_to_group_by_codenames(group, codenames)
        if group.name not in [PII, PII_VIEW]:
            remove_pii_permissions_from_group(group)
        remove_historical_group_permissions(group)
    if verbose:
        sys.stdout.write(style.MIGRATE_HEADING("Done\n"))
        sys.stdout.flush()
