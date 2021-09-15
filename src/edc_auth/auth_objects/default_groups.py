from .codenames import (
    account_manager,
    administration,
    auditor,
    celery_manager,
    clinic,
    clinic_super,
    dispensing,
    everyone,
    pharmacy,
)
from .default_group_names import (
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CELERY_MANAGER,
    CLINIC,
    CLINIC_SUPER,
    DISPENSING,
    EVERYONE,
    PHARMACY,
    PII,
    PII_VIEW,
)

default_groups = {
    ACCOUNT_MANAGER: account_manager,
    ADMINISTRATION: administration,
    AUDITOR: auditor,
    CELERY_MANAGER: celery_manager,
    CLINIC: clinic,
    CLINIC_SUPER: clinic_super,
    DISPENSING: dispensing,
    EVERYONE: everyone,
    PHARMACY: pharmacy,
    PII: [],
    PII_VIEW: [],
}
