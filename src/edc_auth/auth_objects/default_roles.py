from edc_auth.auth_objects.default_role_names import STATISTICIAN

from .default_group_names import (
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CLINIC,
    CLINIC_SUPER,
    EVERYONE,
    PII,
    PII_VIEW,
)
from .default_role_names import (
    ACCOUNT_MANAGER_ROLE,
    AUDITOR_ROLE,
    CLINICIAN_ROLE,
    CLINICIAN_SUPER_ROLE,
    CUSTOM_ROLE,
    NURSE_ROLE,
    STAFF_ROLE,
)

# Format {ROLE_NAME: [GROUP_NAME, GROUP_NAME, ...]
default_roles = {
    ACCOUNT_MANAGER_ROLE: [ACCOUNT_MANAGER],
    AUDITOR_ROLE: [
        AUDITOR,
        PII_VIEW,
    ],
    CLINICIAN_ROLE: [
        CLINIC,
        PII,
    ],
    CLINICIAN_SUPER_ROLE: [
        CLINIC_SUPER,
        CLINIC,
        PII,
    ],
    CUSTOM_ROLE: [],
    NURSE_ROLE: [
        CLINIC,
        PII,
    ],
    STAFF_ROLE: [ADMINISTRATION, EVERYONE],
    STATISTICIAN: [AUDITOR],
}
