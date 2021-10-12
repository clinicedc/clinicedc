from .codenames import (
    account_manager,
    administration,
    auditor,
    celery_manager,
    clinic,
    clinic_super,
    everyone,
)
from .default_group_names import (
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CELERY_MANAGER,
    CLINIC,
    CLINIC_SUPER,
    EVERYONE,
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
    EVERYONE: everyone,
    PII: [],
    PII_VIEW: [],
}
