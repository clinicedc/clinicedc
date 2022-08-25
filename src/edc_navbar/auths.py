from edc_auth.auth_objects import EVERYONE
from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import custom_codename_tuples

site_auths.add_post_update_func(
    "edc_navbar", remove_default_model_permissions_from_edc_permissions
)
site_auths.add_custom_permissions_tuples(
    model="edc_navbar.edcpermissions", codename_tuples=custom_codename_tuples
)

site_auths.update_group(
    "edc_navbar.nav_administration",
    "edc_navbar.nav_home",
    "edc_navbar.nav_logout",
    "edc_navbar.nav_public",
    name=EVERYONE,
)
