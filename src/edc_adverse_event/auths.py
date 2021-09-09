from edc_auth.default_role_names import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    NURSE_ROLE,
    STATISTICIAN_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from .auth_objects import (
    AE,
    AE_REVIEW,
    TMG,
    TMG_REVIEW,
    TMG_ROLE,
    ae,
    ae_review,
    tmg,
    tmg_review,
    tmg_role_group_names,
)

site_auths.add_group(*ae, name=AE)
site_auths.add_group(*ae_review, name=AE_REVIEW)
site_auths.add_group(*tmg, name=TMG)
site_auths.add_group(*tmg_review, name=TMG_REVIEW)
site_auths.add_role(*tmg_role_group_names, name=TMG_ROLE)
site_auths.update_role(AE, name=CLINICIAN_ROLE)
site_auths.update_role(AE, name=NURSE_ROLE)
site_auths.update_role(AE_REVIEW, TMG_REVIEW, name=STATISTICIAN_ROLE)
site_auths.update_role(AE_REVIEW, TMG_REVIEW, name=AUDITOR_ROLE)
site_auths.update_role(AE, TMG, name=DATA_MANAGER_ROLE)
