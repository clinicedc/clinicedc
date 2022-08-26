from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

site_auths.add_post_update_func(
    "edc_subject_dashboard", remove_default_model_permissions_from_edc_permissions
)

SUBJECT_VIEW = "SUBJECT_VIEW"

site_auths.add_custom_permissions_tuples(
    model="edc_subject_dashboard.edcpermissions",
    codename_tuples=(
        ("edc_subject_dashboard.view_subject_listboard", "Can access subject listboard"),
        ("edc_subject_dashboard.nav_subject_section", "Can access nav_subject_section"),
    ),
)

site_auths.add_group(
    "edc_subject_dashboard.view_subject_listboard",
    "edc_subject_dashboard.nav_subject_section",
    name=SUBJECT_VIEW,
)

site_auths.update_role(SUBJECT_VIEW, name=CLINICIAN_ROLE)
site_auths.update_role(SUBJECT_VIEW, name=NURSE_ROLE)
site_auths.update_role(SUBJECT_VIEW, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(SUBJECT_VIEW, name=AUDITOR_ROLE)
