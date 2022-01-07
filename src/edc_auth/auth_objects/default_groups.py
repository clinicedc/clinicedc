from .codenames import account_manager, administration, celery_manager, everyone
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
    AUDITOR: [],
    CELERY_MANAGER: celery_manager,
    CLINIC: [],
    CLINIC_SUPER: [],
    EVERYONE: everyone,
    PII: [],
    PII_VIEW: [],
}
