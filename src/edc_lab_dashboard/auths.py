from edc_auth.site_auths import site_auths
from edc_lab.auth_objects import LAB, LAB_VIEW

from edc_lab_dashboard.auth_objects import (
    lab_dashboard_codenames,
    lab_dashboard_tuples,
    lab_navbar_codenames,
    lab_navbar_tuples,
)

site_auths.update_group(*lab_dashboard_codenames, *lab_navbar_codenames, name=LAB)
site_auths.update_group(*lab_dashboard_codenames, *lab_navbar_codenames, name=LAB_VIEW)
site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.dashboard", codename_tuples=lab_dashboard_tuples
)
site_auths.add_custom_permissions_tuples(
    model="edc_navbar.navbar", codename_tuples=lab_navbar_tuples
)
