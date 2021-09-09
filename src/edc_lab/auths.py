from edc_auth import ADMINISTRATION, EVERYONE, PII_VIEW
from edc_auth.default_role_names import (
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    NURSE_ROLE,
    STATISTICIAN_ROLE,
)
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from .auth_objects import (
    LAB,
    LAB_TECHNICIAN_ROLE,
    LAB_VIEW,
    lab,
    lab_dashboard_tuples,
    lab_view,
)

site_auths.add_group(*lab, name=LAB)
site_auths.add_group(*lab_view, name=LAB_VIEW)
site_auths.add_role(ADMINISTRATION, EVERYONE, LAB, PII_VIEW, name=LAB_TECHNICIAN_ROLE)
site_auths.update_role(LAB, name=CLINICIAN_ROLE)
site_auths.update_role(LAB, name=NURSE_ROLE)
site_auths.update_role(LAB, name=DATA_MANAGER_ROLE)
site_auths.update_role(LAB_VIEW, name=AUDITOR_ROLE)
site_auths.update_role(LAB_VIEW, name=STATISTICIAN_ROLE)
site_auths.add_custom_permissions_tuples(
    model="edc_dashboard.dashboard", codename_tuples=lab_dashboard_tuples
)
