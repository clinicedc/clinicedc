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
    REVIEW,
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
        REVIEW,
    ],
    CLINICIAN_ROLE: [
        CLINIC,
        PII,
        REVIEW,
    ],
    CLINICIAN_SUPER_ROLE: [
        CLINIC_SUPER,
        CLINIC,
        PII,
        REVIEW,
    ],
    CUSTOM_ROLE: [],
    NURSE_ROLE: [
        CLINIC,
        PII,
        REVIEW,
    ],
    PHARMACIST_ROLE: [ADMINISTRATION, EVERYONE, PHARMACY],
    STAFF_ROLE: [ADMINISTRATION, EVERYONE],
    SITE_PHARMACIST_ROLE: [
        DISPENSING,
    ],
}
