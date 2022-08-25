from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import (
    RANDO_BLINDED,
    RANDO_UNBLINDED,
    get_rando_permissions_codenames,
    make_randomizationlist_view_only,
    update_rando_group_permissions,
)

site_auths.add_post_update_func(
    "edc_randomization", remove_default_model_permissions_from_edc_permissions
)

site_auths.add_group(get_rando_permissions_codenames, name=RANDO_BLINDED, view_only=True)
site_auths.add_group(get_rando_permissions_codenames, name=RANDO_UNBLINDED, view_only=True)
site_auths.add_post_update_func("edc_randomization", update_rando_group_permissions)
site_auths.add_post_update_func("edc_randomization", make_randomizationlist_view_only)
