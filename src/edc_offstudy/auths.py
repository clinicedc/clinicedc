from edc_auth.auth_objects import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths

from .auth_objects import OFFSTUDY, OFFSTUDY_SUPER, OFFSTUDY_VIEW, codenames

site_auths.add_group(*codenames, name=OFFSTUDY, no_delete=True)
site_auths.add_group(*codenames, name=OFFSTUDY_SUPER)
site_auths.add_group(*codenames, name=OFFSTUDY_VIEW, view_only=True)
site_auths.update_role(OFFSTUDY, name=CLINICIAN_ROLE)
site_auths.update_role(OFFSTUDY, name=NURSE_ROLE)
site_auths.update_role(OFFSTUDY_SUPER, name=CLINICIAN_SUPER_ROLE)
site_auths.update_role(OFFSTUDY_VIEW, name=AUDITOR_ROLE)
