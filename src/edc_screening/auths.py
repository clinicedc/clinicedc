from edc_auth.site_auths import site_auths

from .auth_objects import SCREENING, SCREENING_ROLE, SCREENING_SUPER, SCREENING_VIEW

site_auths.add_group(
    "edc_dashboard.view_screening_listboard",
    "edc_navbar.nav_screening_section",
    name=SCREENING,
)

site_auths.add_group(
    "edc_dashboard.view_screening_listboard",
    "edc_navbar.nav_screening_section",
    name=SCREENING_SUPER,
)

site_auths.add_group(
    "edc_dashboard.view_screening_listboard",
    "edc_navbar.nav_screening_section",
    name=SCREENING_VIEW,
)

site_auths.add_role(SCREENING, name=SCREENING_ROLE)
