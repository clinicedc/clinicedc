from edc_auth.auth_objects import CELERY_MANAGER
from edc_auth.site_auths import site_auths

from .auth_objects import (
    DATA_MANAGER,
    DATA_MANAGER_EXPORT,
    DATA_MANAGER_ROLE,
    DATA_QUERY,
    SITE_DATA_MANAGER_ROLE,
    data_manager,
    data_query,
)

# groups
site_auths.add_group(*data_manager, name=DATA_MANAGER)
site_auths.add_group(*data_query, name=DATA_QUERY)
site_auths.add_group(
    "edc_data_manager.export_datadictionary",
    "edc_data_manager.export_dataquery",
    "edc_data_manager.export_queryrule",
    name=DATA_MANAGER_EXPORT,
)

# roles
site_auths.add_role(CELERY_MANAGER, DATA_MANAGER, name=DATA_MANAGER_ROLE)
site_auths.add_role(DATA_QUERY, name=SITE_DATA_MANAGER_ROLE)
