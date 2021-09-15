from edc_auth.auth_objects.default_role_names import STATISTICIAN

from .default_group_names import (
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CLINIC,
    CLINIC_SUPER,
    DISPENSING,
    EVERYONE,
    PHARMACY,
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
    PHARMACIST_ROLE,
    SITE_PHARMACIST_ROLE,
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
    PHARMACIST_ROLE: [ADMINISTRATION, EVERYONE, PHARMACY],
    STAFF_ROLE: [ADMINISTRATION, EVERYONE],
    SITE_PHARMACIST_ROLE: [
        DISPENSING,
    ],
    STATISTICIAN: [],
}
