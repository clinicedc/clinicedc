from edc_auth.site_auths import site_auths

from .auth_objects import (
    add_edc_dashboard_permissions,
    remove_permissions_to_edc_dashboard_model,
)

site_auths.add_post_update_func(add_edc_dashboard_permissions)
site_auths.add_post_update_func(remove_permissions_to_edc_dashboard_model)
