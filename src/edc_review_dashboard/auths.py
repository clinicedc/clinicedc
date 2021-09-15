from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths

from .auth_objects import REVIEW

site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.dashboard",
    codename_tuples=[
        (
            "edc_dashboard.view_subject_review_listboard",
            "Can view Subject review listboard",
        )
    ],
)
site_auths.add_group("edc_dashboard.view_subject_review_listboard", name=REVIEW)
site_auths.update_role(REVIEW, name=AUDITOR_ROLE)
site_auths.update_role(REVIEW, name=CLINICIAN_ROLE)
site_auths.update_role(REVIEW, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(REVIEW, name=NURSE_ROLE)
