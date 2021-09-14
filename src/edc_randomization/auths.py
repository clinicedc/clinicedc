from edc_auth.auth_objects import PHARMACIST_ROLE, SITE_PHARMACIST_ROLE
from edc_auth.site_auths import site_auths

from .auth_objects import (
    export_rando,
    get_rando_permissions_codenames,
    make_randomizationlist_view_only,
    update_rando_group_permissions,
)
from .constants import EXPORT_RANDO, RANDO

site_auths.add_group(*export_rando, name=EXPORT_RANDO)
site_auths.add_group(get_rando_permissions_codenames, name=RANDO)
site_auths.update_role(RANDO, name=PHARMACIST_ROLE)
site_auths.update_role(RANDO, name=SITE_PHARMACIST_ROLE)
site_auths.add_post_update_func(update_rando_group_permissions)
site_auths.add_post_update_func(make_randomizationlist_view_only)
