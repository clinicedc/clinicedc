from edc_auth.site_auths import site_auths

from .auth_objects import (
    create_edc_navbar_permissions,
    remove_permissions_to_edc_navbar_model,
)

site_auths.add_pre_update_func(create_edc_navbar_permissions)
site_auths.add_post_update_func(remove_permissions_to_edc_navbar_model)
