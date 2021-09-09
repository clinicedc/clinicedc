import sys

from edc_auth.default_role_names import PHARMACIST_ROLE, SITE_PHARMACIST_ROLE
from edc_auth.site_auths import site_auths

from .auth_objects import get_rando_permissions_codenames, get_rando_permissions_tuples
from .constants import EXPORT_RANDO, RANDO
from .site_randomizers import site_randomizers

# codenames
export_rando = [
    "edc_dashboard.view_export_dashboard",
    "edc_export.show_export_admin_action",
    "edc_randomization.export_randomizationlist",
]


# post_update_func
def update_rando_group_permissions(auth_updater):
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


def make_randomizationlist_view_only(auth_updater):
    for randomizer_cls in site_randomizers._registry.values():
        app_label, model = randomizer_cls.model_cls(
            apps=auth_updater.apps
        )._meta.label_lower.split(".")
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
            )


site_auths.add_group(*export_rando, name=EXPORT_RANDO)
site_auths.add_group(get_rando_permissions_codenames, name=RANDO)
site_auths.update_role(RANDO, name=PHARMACIST_ROLE)
site_auths.update_role(RANDO, name=SITE_PHARMACIST_ROLE)
site_auths.add_post_update_func(update_rando_group_permissions)
site_auths.add_post_update_func(make_randomizationlist_view_only)
