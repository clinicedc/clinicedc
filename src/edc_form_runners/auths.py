from edc_auth.constants import AUDITOR_ROLE, CLINICIAN_ROLE
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from .auth_objects import (
    EDC_FORM_RUNNERS,
    EDC_FORM_RUNNERS_SUPER,
    EDC_FORM_RUNNERS_VIEW,
    codenames,
)


def update_site_auths():
    site_auths.add_group(*codenames, name=EDC_FORM_RUNNERS_VIEW, view_only=True)
    site_auths.add_group(*codenames, name=EDC_FORM_RUNNERS, no_delete=True)
    site_auths.add_group(*codenames, name=EDC_FORM_RUNNERS_SUPER)

    site_auths.update_role(EDC_FORM_RUNNERS_VIEW, name=AUDITOR_ROLE)
    site_auths.update_role(EDC_FORM_RUNNERS, name=CLINICIAN_ROLE)
    site_auths.update_role(EDC_FORM_RUNNERS_SUPER, name=DATA_MANAGER_ROLE)


update_site_auths()
