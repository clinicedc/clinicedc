from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions
from edc_lab.auth_objects import LAB, LAB_VIEW

from edc_lab_dashboard.auth_objects import (
    lab_dashboard_codenames,
    lab_dashboard_tuples,
    lab_navbar_codenames,
    lab_navbar_tuples,
)

site_auths.add_post_update_func(
    "edc_lab_dashboard", remove_default_model_permissions_from_edc_permissions
)

site_auths.add_custom_permissions_tuples(
    model="edc_lab_dashboard.edcpermissions", codename_tuples=lab_navbar_tuples
)
site_auths.add_custom_permissions_tuples(
    model="edc_lab_dashboard.edcpermissions", codename_tuples=lab_dashboard_tuples
)

site_auths.update_group(*lab_dashboard_codenames, *lab_navbar_codenames, name=LAB)
site_auths.update_group(*lab_dashboard_codenames, *lab_navbar_codenames, name=LAB_VIEW)
