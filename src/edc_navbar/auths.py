from edc_auth.auth_objects import AUDITOR, CLINIC, EVERYONE
from edc_auth.site_auths import site_auths

from .auth_objects import navbar_tuples, remove_permissions_to_edc_navbar_model

site_auths.add_post_update_func(remove_permissions_to_edc_navbar_model)
site_auths.add_custom_permissions_tuples(
    model="edc_navbar.navbar", codename_tuples=navbar_tuples
)
site_auths.update_group(
    "edc_navbar.nav_screening_section", "edc_navbar.nav_subject_section", name=AUDITOR
)
site_auths.update_group(
    "edc_navbar.nav_screening_section", "edc_navbar.nav_subject_section", name=CLINIC
)

site_auths.update_group(
    "edc_navbar.nav_administration",
    "edc_navbar.nav_home",
    "edc_navbar.nav_logout",
    "edc_navbar.nav_public",
    name=EVERYONE,
)
