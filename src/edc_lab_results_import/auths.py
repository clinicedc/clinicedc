from edc_auth.constants import CLINICIAN_ROLE
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from .auth_objects import LAB_RESULTS_IMPORT, codenames


def update_site_auths():
    site_auths.add_group(*codenames, name=LAB_RESULTS_IMPORT)
    site_auths.update_role(LAB_RESULTS_IMPORT, name=CLINICIAN_ROLE)
    site_auths.update_role(LAB_RESULTS_IMPORT, name=DATA_MANAGER_ROLE)


update_site_auths()
