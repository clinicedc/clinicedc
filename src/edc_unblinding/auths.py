from edc_adverse_event.auth_objects import TMG_ROLE
from edc_auth.default_role_names import CLINICIAN_ROLE, NURSE_ROLE
from edc_auth.site_auths import site_auths

from .auth_objects import (
    UNBLINDING_REQUESTORS,
    UNBLINDING_REQUESTORS_ROLE,
    UNBLINDING_REVIEWERS,
    UNBLINDING_REVIEWERS_ROLE,
    unblinding_requestors,
    unblinding_reviewers,
)

site_auths.add_group(*unblinding_requestors, name=UNBLINDING_REQUESTORS)
site_auths.add_group(*unblinding_reviewers, name=UNBLINDING_REVIEWERS)
site_auths.add_role(UNBLINDING_REQUESTORS, name=UNBLINDING_REQUESTORS_ROLE)
site_auths.add_role(UNBLINDING_REVIEWERS, name=UNBLINDING_REVIEWERS_ROLE)
site_auths.update_role(UNBLINDING_REQUESTORS, name=CLINICIAN_ROLE)
site_auths.update_role(UNBLINDING_REQUESTORS, name=NURSE_ROLE)
site_auths.update_role(UNBLINDING_REQUESTORS, name=TMG_ROLE)
