from edc_auth import (
    ADMINISTRATION,
    CELERY_MANAGER,
    CLINIC,
    EVERYONE,
    PII,
    REVIEW,
    SCREENING,
)
from edc_auth.default_role_names import CLINICIAN_ROLE, NURSE_ROLE, STATISTICIAN_ROLE
from edc_auth.site_auths import site_auths

from .auth_objects import (
    DATA_MANAGER,
    DATA_MANAGER_ROLE,
    DATA_QUERY,
    SITE_DATA_MANAGER,
    SITE_DATA_MANAGER_ROLE,
    data_manager,
    data_query,
)

site_auths.add_group(*data_manager, name=DATA_MANAGER)
site_auths.add_group(*data_query, name=DATA_QUERY)
site_auths.add_role(
    ADMINISTRATION, EVERYONE, REVIEW, SITE_DATA_MANAGER, name=SITE_DATA_MANAGER_ROLE
)
site_auths.add_role(
    ADMINISTRATION,
    CELERY_MANAGER,
    CLINIC,
    DATA_MANAGER,
    EVERYONE,
    PII,
    REVIEW,
    SCREENING,
    name=DATA_MANAGER_ROLE,
)
site_auths.update_role(DATA_QUERY, name=CLINICIAN_ROLE)
site_auths.update_role(DATA_QUERY, name=NURSE_ROLE)
site_auths.update_role(DATA_MANAGER, name=STATISTICIAN_ROLE)
