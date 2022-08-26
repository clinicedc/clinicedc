from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths

from .auth_objects import LISTBOARD

site_auths.update_role(LISTBOARD, name=AUDITOR_ROLE)
site_auths.update_role(LISTBOARD, name=CLINICIAN_ROLE)
site_auths.update_role(LISTBOARD, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(LISTBOARD, name=NURSE_ROLE)
