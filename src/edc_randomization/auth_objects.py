import sys
from typing import Optional

from .site_randomizers import site_randomizers

RANDO_UNBLINDED = "RANDO_UNBLINDED"
RANDO_BLINDED = "RANDO_BLINDED"


def get_rando_permissions_tuples() -> list:
    """Returns a list of tuples, [(codename, description), ...]"""
    rando_tuples = []
    for randomizer_cls in site_randomizers._registry.values():
        app_label, model = randomizer_cls.model_cls()._meta.label_lower.split(".")
        verbose_name = randomizer_cls.model_cls()._meta.verbose_name
        rando_tuples.append((f"{app_label}.view_{model}", f"Can view {verbose_name}"))
        if not randomizer_cls.is_blinded_trial:
            rando_tuples.append(
                (
                    f"{app_label}.display_{model}",
                    f"Can display {verbose_name} assignment",
                )
            )
    return rando_tuples


def get_rando_permissions_codenames() -> list:
    """Returns a list of codenames"""
    return [c[0] for c in get_rando_permissions_tuples()]


# codenames
export_rando = [
    "edc_randomization.export_randomizationlist",
]


# post_update_func
def update_rando_group_permissions(auth_updater, app_label: Optional[str]):
    """Update group permissions for each registered randomizer class."""
    for randomizer_cls in site_randomizers._registry.values():
        if auth_updater.verbose:
            sys.stdout.write(
                "     - creating permissions for registered randomizer_cls "
                f"`{randomizer_cls.name}` model "
                f"`{randomizer_cls.model_cls()._meta.label_lower}`\n"
            )
        rando_tuples = [
            (k, v)
            for k, v in get_rando_permissions_tuples()
            if k.startswith(randomizer_cls.model_cls()._meta.label_lower.split(".")[0])
        ]
        auth_updater.group_updater.create_permissions_from_tuples(
            randomizer_cls.model_cls()._meta.label_lower,
            rando_tuples,
        )


def make_randomizationlist_view_only(auth_updater, app_label: Optional[str]):
    for randomizer_cls in site_randomizers._registry.values():
        randomizer_cls.apps = auth_updater.apps
        app_label, model = randomizer_cls.model_cls()._meta.label_lower.split(".")
        permissions = auth_updater.group_updater.permission_model_cls.objects.filter(
            content_type__app_label=app_label, content_type__model=model
        ).exclude(codename=f"view_{model}")
        codenames = [f"{app_label}.{o.codename}" for o in permissions]
        codenames.extend(
            [
                f"{app_label}.add_{model}",
                f"{app_label}.change_{model}",
                f"{app_label}.delete_{model}",
            ]
        )
        codenames = list(set(codenames))
        for group in auth_updater.group_updater.group_model_cls.objects.all():
            auth_updater.group_updater.remove_permissions_by_codenames(
                group=group,
                codenames=codenames,
                allow_multiple_objects=True,
            )
