from edc_auth.auth_objects import (
    AUDITOR,
    CELERY_MANAGER,
    CLINIC,
    CLINICIAN_ROLE,
    NURSE_ROLE,
    PII,
    REVIEW,
)
from edc_auth.site_auths import site_auths
from edc_export.auth_objects import EXPORT
from edc_screening.auth_objects import SCREENING

from .auth_objects import (
    DATA_MANAGER,
    DATA_MANAGER_ROLE,
    DATA_QUERY,
    SITE_DATA_MANAGER_ROLE,
    data_manager,
    data_query,
)

site_auths.add_group(*data_manager, name=DATA_MANAGER)
site_auths.add_group(*data_query, name=DATA_QUERY)
site_auths.update_group(
    "edc_data_manager.export_datadictionary",
    "edc_data_manager.export_dataquery",
    "edc_data_manager.export_queryrule",
    name=EXPORT,
)
site_auths.add_role(
    AUDITOR,
    REVIEW,
    DATA_QUERY,
    name=SITE_DATA_MANAGER_ROLE,
)
site_auths.add_role(
    CELERY_MANAGER,
    CLINIC,
    DATA_MANAGER,
    PII,
    REVIEW,
    SCREENING,
    name=DATA_MANAGER_ROLE,
)
site_auths.update_role(DATA_QUERY, name=CLINICIAN_ROLE)
site_auths.update_role(DATA_QUERY, name=NURSE_ROLE)
