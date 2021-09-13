from edc_adverse_event.auth_objects import TMG_ROLE
from edc_auth.auth_objects import AUDITOR_ROLE, CLINICIAN_ROLE, NURSE_ROLE
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE, SITE_DATA_MANAGER_ROLE

from .auth_objects import (
    ACTION_ITEM,
    ACTION_ITEM_VIEW_ONLY,
    action_items_codenames,
    action_items_view_only_codenames,
    navbar_tuples,
)

site_auths.add_group(*action_items_codenames, name=ACTION_ITEM)
site_auths.add_group(*action_items_view_only_codenames, name=ACTION_ITEM_VIEW_ONLY)
site_auths.update_role(ACTION_ITEM, name=CLINICIAN_ROLE)
site_auths.update_role(ACTION_ITEM, name=NURSE_ROLE)
site_auths.update_role(ACTION_ITEM_VIEW_ONLY, name=AUDITOR_ROLE)
site_auths.update_role(ACTION_ITEM, name=TMG_ROLE)
site_auths.update_role(ACTION_ITEM, name=DATA_MANAGER_ROLE)
site_auths.update_role(ACTION_ITEM, name=SITE_DATA_MANAGER_ROLE)

site_auths.add_custom_permissions_tuples(
    model="edc_navbar.navbar", codename_tuples=navbar_tuples
)
