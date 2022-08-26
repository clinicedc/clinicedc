from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

REVIEW = "REVIEW"

site_auths.add_post_update_func(
    "edc_review_dashboard", remove_default_model_permissions_from_edc_permissions
)

site_auths.add_custom_permissions_tuples(
    model="edc_review_dashboard.edcpermissions",
    codename_tuples=[
        (
            "edc_review_dashboard.view_subject_review_listboard",
            "Can access subject review listboard",
        )
    ],
)
site_auths.add_group("edc_review_dashboard.view_subject_review_listboard", name=REVIEW)

site_auths.update_role(REVIEW, name=AUDITOR_ROLE)
site_auths.update_role(REVIEW, name=CLINICIAN_ROLE)
site_auths.update_role(REVIEW, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(REVIEW, name=NURSE_ROLE)
