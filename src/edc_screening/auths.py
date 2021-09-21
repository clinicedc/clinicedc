from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
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
site_auths.update_role(SCREENING, name=CLINICIAN_ROLE)
site_auths.update_role(SCREENING, name=NURSE_ROLE)
site_auths.update_role(SCREENING_SUPER, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(SCREENING_VIEW, name=AUDITOR_ROLE)
