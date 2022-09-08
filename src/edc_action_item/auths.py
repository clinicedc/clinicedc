from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import (
    ACTION_ITEM,
    ACTION_ITEM_EXPORT,
    ACTION_ITEM_VIEW_ONLY,
    action_items_codenames,
    navbar_tuples,
)

site_auths.add_post_update_func(
    "edc_action_item",
    remove_default_model_permissions_from_edc_permissions,
)

site_auths.add_custom_permissions_tuples(
    model="edc_action_item.edcpermissions", codename_tuples=navbar_tuples
)

site_auths.add_group(*action_items_codenames, name=ACTION_ITEM)
site_auths.add_group(*action_items_codenames, name=ACTION_ITEM_VIEW_ONLY, view_only=True)
site_auths.add_group(
    "edc_action_item.export_actionitem",
    "edc_action_item.export_actiontype",
    "edc_action_item.export_historicalactionitem",
    name=ACTION_ITEM_EXPORT,
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

site_auths.update_role(ACTION_ITEM, name=CLINICIAN_ROLE)
site_auths.update_role(ACTION_ITEM, name=NURSE_ROLE)
site_auths.update_role(ACTION_ITEM, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(ACTION_ITEM_VIEW_ONLY, name=AUDITOR_ROLE)
