from edc_auth.site_auths import site_auths

from .auth_objects import (
    ACTION_ITEM,
    ACTION_ITEM_VIEW_ONLY,
    action_items_codenames,
    navbar_tuples,
)

site_auths.add_group(*action_items_codenames, name=ACTION_ITEM)
site_auths.add_group(*action_items_codenames, name=ACTION_ITEM_VIEW_ONLY, view_only=True)
site_auths.add_custom_permissions_tuples(
    model="edc_navbar.navbar", codename_tuples=navbar_tuples
)

site_auths.add_custom_permissions_tuples(
    model="edc_action_item.historicalactionitem",
    codename_tuples=[
        (
            "edc_action_item.export_historicalactionitem",
            "Cane export historicalactionitem",
        ),
        (
            "edc_action_item.export_historicalreference",
            "Cane export historicalreference",
        ),
    ],
)
