from edc_auth.site_auths import site_auths

from .auth_objects import SCREENING

site_auths.add_group(
    "edc_dashboard.view_screening_listboard",
    "edc_navbar.nav_screening_section",
    name=SCREENING,
)
