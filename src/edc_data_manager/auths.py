from edc_auth.auth_objects import (
    CELERY_MANAGER,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    NURSE_ROLE,
)
from edc_auth.site_auths import site_auths

from .auth_objects import (
    DATA_MANAGER,
    DATA_MANAGER_EXPORT,
    DATA_MANAGER_ROLE,
    DATA_QUERY,
    DATA_QUERY_VIEW,
    SITE_DATA_MANAGER_ROLE,
    data_manager,
)

# groups
site_auths.add_group(*data_manager, name=DATA_MANAGER)
site_auths.add_group(*data_manager, name=DATA_QUERY_VIEW, view_only=True)

site_auths.add_group(*data_manager, name=DATA_QUERY, view_only=True)
site_auths.update_group("edc_data_manager.change_dataquery", name=DATA_QUERY)

site_auths.add_group(
    "edc_data_manager.export_datadictionary",
    "edc_data_manager.export_dataquery",
    "edc_data_manager.export_queryrule",
    name=DATA_MANAGER_EXPORT,
)

# roles
site_auths.add_role(CELERY_MANAGER, DATA_MANAGER, name=DATA_MANAGER_ROLE)
site_auths.add_role(DATA_QUERY, name=SITE_DATA_MANAGER_ROLE)
site_auths.update_role(DATA_QUERY, name=CLINICIAN_ROLE)
site_auths.update_role(DATA_QUERY, name=NURSE_ROLE)
site_auths.update_role(DATA_QUERY, name=CLINICIAN_SUPER_ROLE)
