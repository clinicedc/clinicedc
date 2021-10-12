from edc_auth.site_auths import site_auths

from .auth_objects import (
    RANDO_UNBLINDED,
    RANDO_VIEW,
    get_rando_permissions_codenames,
    make_randomizationlist_view_only,
    update_rando_group_permissions,
)

site_auths.add_group(get_rando_permissions_codenames, name=RANDO_VIEW, view_only=True)
site_auths.add_group(get_rando_permissions_codenames, name=RANDO_UNBLINDED)
site_auths.add_post_update_func(update_rando_group_permissions)
site_auths.add_post_update_func(make_randomizationlist_view_only)
