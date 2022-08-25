from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import dashboard_tuples

site_auths.add_post_update_func(
    "edc_dashboard", remove_default_model_permissions_from_edc_permissions
)


site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.edcpermissions", codename_tuples=dashboard_tuples
)
