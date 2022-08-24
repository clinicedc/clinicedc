from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths

from .auth_objects import LISTBOARD

site_auths.add_custom_permissions_tuples(
    model="edc_listboard.listboard",
    codename_tuples=(
        ("edc_listboard.view_screening_listboard", "Can view Screening listboard"),
        ("edc_listboard.view_subject_listboard", "Can view Subject listboard"),
    ),
)

site_auths.add_group(
    "edc_listboard.view_screening_listboard",
    "edc_listboard.view_subject_listboard",
    name=LISTBOARD,
)

site_auths.update_role(LISTBOARD, name=AUDITOR_ROLE)
site_auths.update_role(LISTBOARD, name=CLINICIAN_ROLE)
site_auths.update_role(LISTBOARD, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(LISTBOARD, name=NURSE_ROLE)
