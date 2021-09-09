from edc_auth.site_auths import site_auths

from .auth_objects import dashboard_tuples, remove_permissions_to_edc_dashboard_model

site_auths.add_post_update_func(remove_permissions_to_edc_dashboard_model)
site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.dashboard", codename_tuples=dashboard_tuples
)
